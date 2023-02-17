#!/usr/bin/env python3
# vim: shiftwidth=4 tabstop=4 expandtab textwidth=0
# Copyright (c) 2023 stuart.lynne@gmail.com

__version__ = "0.1.0"

import os
import sys
import csv
import argparse
import itertools
from math import isnan
import datetime

from fit_tool.data_message import DataMessage
from fit_tool.fit_file import FitFile
from fit_tool.base_type import BaseType
from fit_tool.profile.profile_type import AntplusDeviceType

import time
import sys

def bytes2str(bytes):
    return ' '.join(str('%02x'%b) for b in bytes)

class CSVWriter:
    def __init__(self, pathname=None, fieldnames=None):
        self.fieldnames = fieldnames
        #print('CSVWriter[%s] %s' % (pathname, fieldnames,), file=sys.stderr)
        self.f = open(f"{pathname}.csv", 'w', newline='')
        self.writer = csv.DictWriter(self.f, self.fieldnames, extrasaction='ignore')
        self.writer.writeheader()

    def writerow(self, row=None):
        self.writer.writerow(row)

# is_valid - is field value valid
#   - not None
#   - if float, not isnan
#   - not equal to basetype invalid raw value
# Deprecated, waiting for fit_tool version to update
#   - not float version of basetype invalid raw value
def xis_valid(i, f, v):
    if v is None:
        print('is_valid[%d]: %s: v: %s INVALID' % (i, f.name, v), file=sys.stderr)
        return False
    if f.base_type in [BaseType.FLOAT32, BaseType.FLOAT64, ] and isnan(v):
        print('is_valid[%d]: %s: isnan v: %s INVALID' % (i, f.name, v), file=sys.stderr)
        return False
    if v == f.base_type.invalid_raw_value():
        print('is_valid[%d]: %s: invalid_raw_value: %s v: %s INVALID' % (i, f.name, f.base_type.invalid_raw_value(), v), file=sys.stderr)
        return False
    if v == float(f.base_type.invalid_raw_value()):
        print('is_valid[%d]: %s: float(invalid_raw_value): %s v: %s INVALID' % (i, f.name, float(f.base_type.invalid_raw_value()), v), file=sys.stderr)
        return False
    print('is_valid[%d]: %s: base_type: %s v: %s %s VALID' % (i, f.name, f.base_type.name, v, type(v)), file=sys.stderr)
    return True


def is_valid(i, f, v):
    #print('%s: is_valid: %s v: %s:%s' % (f.name, f.base_type.invalid_raw_value(), v, type(v)), file=sys.stderr)
    if f.base_type in [BaseType.FLOAT32, BaseType.FLOAT64, ]:
        #print('is_valid: %s: invalid_raw_value: %s v: %s FLOAT ISNAN: %s' % (f.name, f.base_type.invalid_raw_value(), v, isnan(v)), file=sys.stderr)
        return not isnan(v)
    if v is None:
        return False
    if v == f.base_type.invalid_raw_value():
        print('is_valid: %s: invalid_raw_value: %s v: %s INVALID' % (f.name, f.base_type.invalid_raw_value(), v), file=sys.stderr)
        return False
    if v == float(f.base_type.invalid_raw_value()):
        print('is_valid: %s: float(invalid_raw_value): %s v: %s INVALID' % (f.name, float(f.base_type.invalid_raw_value()), v), file=sys.stderr)
        return False
    #print('is_valid: %s: invalid_raw_value: %s:%s v: %s:%s VALID' % (
    #    f.name, f.base_type.invalid_raw_value(), type(f.base_type.invalid_raw_value()), v, type(v)), file=sys.stderr)
    return True

# XXX 
# current fit_tool does not do this correctly, see python_fit_tool issue #9
# These are copies of field.get_values() and field.decode_value(). The
# only change is to add the test for:
#   encoded_value == f.base_type.invalid_raw_value()
# 
def fit_field_decode_value(f, encoded_value, sub_field=None):
    if encoded_value is None or type(encoded_value) == str:
        return encoded_value

    # without this we see (for example) time 655.36 in hrv messages
    if encoded_value == f.base_type.invalid_raw_value():
        return None

    scale = f.get_scale(sub_field=sub_field)
    offset = f.get_offset(sub_field=sub_field)

    if (scale is None or scale == 1.0) and (offset is None or offset == 0.0):
        # no scaling
        value = encoded_value
    else:
        scale = scale if scale is not None else 1.0
        offset = offset if offset is not None else 0.0

        value = f.un_scale_offset_value(encoded_value, scale, offset)
        if f.type_name == 'date_time':
            value = round(value)

    return value

def fit_field_get_values(f):
    return [fit_field_decode_value(f, encoded_value) for encoded_value in f.encoded_values]

# get_messages - load FIT messages from a file
def get_messages(pathname,):
    record_standard = {0:[]}
    record_developer = {0:[]}
    hrv_standard = {0:[]}
    hrv_developer = {0:[]}
    device_info_dict = {}
    fit_file = FitFile.from_file(pathname)
    messages = []
    # iterate across all of the Data Messages
    for i, record in enumerate(fit_file.records):
        if not isinstance(record.message, DataMessage):
            continue
        fields = {}
        for f in itertools.chain(record.message.fields, record.message.developer_fields):
            if not f.is_valid():
                continue
            # try for list, 
            try:
                # build list of values, testing for None, NaN and invalid raw value
                #v = [ v for v in f.get_values() if is_valid(i, f, v)]
                v = [ v for v in fit_field_get_values(f) if is_valid(i, f, v)]

                # ignore fields with no valid values
                if len(v) == 0:
                    continue

                # save only v[0] if only one value else the list
                fields[f.name] = v[0] if len(v) == 1 else v

            # possibly not a list
            except KeyError:
                v = f.get_value()
                fields[f.name] = v

        # save device info separately
        if record.message.NAME == 'device_info':
            device_index = fields['device_index']
            device_info_dict[device_index] = fields
             
        device_index = fields.get('device_index',0 )
        messages.append((record.message.NAME, ('device_index', device_index), fields))
    
    return device_info_dict, messages


# extract fields in fields_arg from message_name messages, dump to csv file
#
def extract(pathname=None, messages=None, device_index=0, message_name=None, fields_arg=None, fieldnames=None, args=None, ):

    # if fields_args is available we split that and use it for fieldnames.
    # default is to use provided fieldnames (all fieldnames for the device)
    if fields_arg is not None:
        if args.verbose:
            print('extract[%s:%s]: %s' % (device_index, message_name, fields_arg), file=sys.stderr)
        fieldnames = fields_arg.split(',') if fields_arg != '--' else None
    if args.verbose:
        print('extract[%s:%s]: %s' % (device_index, message_name, fieldnames), file=sys.stderr)

    # construct csv file name by adding fields names
    fields_str = ''.join(f"-{f}" for f in fieldnames)
    path, ext = os.path.splitext(pathname)
    fout_name = f"{path}-{message_name}-{fields_str}"
    if args.expand:
        fout_name += "-ex"

    if args.verbose:
        print('extract[%s:%s]: %s' % (device_index, message_name, fout_name), file=sys.stderr)
        print('extract[%s:%s]: no_datestamp: %s timestamp: %s expand: %s' % (
            device_index, message_name, args.no_datestamp, args.timestamp, args.expand), file=sys.stderr)

    # set csv_fieldnames to be fieldnames, add timestamp and datestamp if needed, create CSV Writer
    csv_fieldnames = fieldnames 
    if message_name != 'hrv':
        if not args.timestamp and 'timestamp' in csv_fieldnames:
            csv_fieldnames.remove('timestamp')
        if not args.no_datestamp:
            csv_fieldnames.insert(0, 'datestamp')
    csvwriter = CSVWriter(pathname=fout_name, fieldnames = csv_fieldnames, )

    # iterate across the messages list
    for name, device_index_info, fields in messages:

        # get the device index for the message, default is 0 if none found, 
        # continue if not the one we are looking for.
        message_device_index = fields.get('device_index', 0)
        if device_index is not None and device_index != message_device_index:
            #print('[%d:%d:%s] fields: %s NOT DEVICE_INDEX' % (device_index, message_device_index, name, fields), file=sys.stderr)
            continue

        # continue if name of record is not the message name we want
        if message_name is not None and message_name != name:
            #print('[%d:%s] fields: %s NOT MESSAGE_NAME' % (device_index, name, fields), file=sys.stderr)
            continue
        
        # build a values dictionary, add timestamp and datestamp if needed
        values = { f: fields[f] for f in fieldnames if f in fields } 
        timestamp = int(fields['timestamp']/1000) if 'timestamp' in fields else None
        datestamp = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S') if timestamp is not None else None
            
        # if expand flag is not set fields that are multiple values are put into single csv cell as "[..,..]"
        if not args.expand:
            if values != {}:
                values['timestamp'] = timestamp
                values['datestamp'] = datestamp
                #print('[%5d:%d:%s] values: %s FALSE' % (device_index, message_name, values), file=sys.stderr)
                csvwriter.writerow(values)
            continue

        # if expand flag is set then fields that are multiple values are inserted over multiple lines
        finished = False
        while not finished:
            # assume finished, until and unless we see something too continue looping
            finished = True
            row = {}
            for k, v in values.items():
                if v is None:
                    pass
                elif isinstance(v, list) and len(v) > 0:
                    row[k] = v.pop(0)
                    # if this list is not empty then we are not finished
                    if len(v) > 0:
                        finished = False
                else:
                    row[k] = v
                    values[k] = None
            if row == {}:
                continue
            row['timestamp'] = timestamp
            row['datestamp'] = datestamp
            #print('[%d:%s] values: %s finished: %s' % (device_index, message_name, row, finished), file=sys.stderr)
            csvwriter.writerow(row)

# fields - get a list of all fields for each message for each device
#
def fields(messages, args=None):
    device_fields = {}

    for i, m in enumerate(messages):
        record_name, device_index, fields = m
        device_index = device_index[1]
        if device_index not in device_fields:
            device_fields[device_index] = {}

        if record_name not in device_fields[device_index]:
            device_fields[device_index][record_name] = {}

        field_names = device_fields[device_index][record_name]

        #print('[%5d] %s' % (i, m), file=sys.stderr)
        for k in fields.keys():
            field_names[k] = True

    if args.verbose:
        print('Fields', file=sys.stderr)
        for k1, v1 in device_fields.items():
            for k2, v2 in v1.items():
                print('[%2d:%24s] %s' % (k1, k2, [k3 for k3 in v2.keys()]), file=sys.stderr)

    return device_fields

def main():
    parser = argparse.ArgumentParser(description='fitextract', epilog='Extract Hrv or Record data fields to CSV file')
    parser.add_argument('--hrv', help='Extract Hrv Message time field', action='store_true')
    parser.add_argument('--record', type=str, help='Extract Hrv Message fields')
    parser.add_argument('--device_index', '--di', type=int, help='device_index to extract, default is None')
    parser.add_argument('--expand', help='Expand arrays to multiple rows', action='store_true')
    parser.add_argument('--timestamp', help='Do not add Timestamp if time available', action='store_true')
    parser.add_argument('--no-datestamp', help='Do not Add Datestamp if time available', action='store_true')
    parser.add_argument('-v', '--verbose', help='Extra Debug on stderr', action='store_true')
    parser.add_argument('-V', '--version', help='Version', action='store_true')
    parser.add_argument('fitfile', nargs='*',  type=str, help='FIT File')
    args = parser.parse_args()
    print('main: args: %s' % (args), file=sys.stderr)
    if args.version:
        print(f"fitextract {__version__}", file=sys.stderr)


    # iterate across files to extract from, extract hrv and record messages separately
    if args.fitfile is None:
        return

    for p in args.fitfile:

        device_info_dict, messages = get_messages(p, )
        if args.verbose:
            print('', file=sys.stderr) 
            print('Devices: ', file=sys.stderr) 
            for k1, v1 in device_info_dict.items():
                d = v1.get('descriptor', '')
                print('[%2d:%24s]: %s' % (k1, v1.get('descriptor', ''), 
                    {k2: v2 for k2, v2 in v1.items() if k2 not in ['timestamp', 'device_index']},
                    ), file=sys.stderr) 

        device_fields_dict = fields(messages, args=args, )

        # 
        for k1, v1 in device_info_dict.items():

            print('', file=sys.stderr) 
            if args.device_index is not None and args.device_index != k1:
                print('[%s: %24s] Skipping device' % (k1, v1.get('descriptor', '')), file=sys.stderr) 
                continue

            if k1 not in device_fields_dict:
                print('[%s: %24s] No fields found' % (k1, v1.get('descriptor', '')), file=sys.stderr) 
                continue

            device_fields = device_fields_dict[k1]

            print('[%s: %24s] Processing records' % (k1, v1.get('descriptor', '')), file=sys.stderr) 

            for k2, v2 in device_fields.items():

                #print('[%s: %24s] k2: %s v2: %s' % (k1, v1.get('descriptor', ''), k2, v2), file=sys.stderr) 

                if k2 == 'hrv' and args.hrv:
                    print('[%s: %24s] HRV fields: %s' % (k1, v1.get('descriptor', ''), v2), file=sys.stderr) 
                    extract(pathname=p, messages=messages, device_index=k1, message_name='hrv', 
                        fieldnames=[k for k in v2.keys()], args=args, )
                    continue

                if k2 == 'record' and args.record is not None:
                    print('[%s: %24s] RECORD fields: %s' % (k1, v1.get('descriptor', ''), v2), file=sys.stderr) 
                    if args.record in ['all', '-', ]:
                        extract(pathname=p, messages=messages, device_index=k1, message_name='record', 
                            fieldnames=[k for k in v2.keys()], args=args, )
                    elif args.record is not None:
                        extract(pathname=p, messages=messages, device_index=args.device_index, message_name='record', 
                            fields_arg=args.record, args=args, )
                    continue

                print('[%s: %24s] SKIPPING %s fields: %s' % (k1, v1.get('descriptor', ''), k2, v2), file=sys.stderr) 
if __name__ == "__main__":
    main()
