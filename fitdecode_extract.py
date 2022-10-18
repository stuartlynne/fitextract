#!/usr/bin/env python3
# vim: shiftwidth=4 tabstop=4 expandtab textwidth=0

import os
import sys
import csv
import argparse
import itertools
import fitdecode


# extract fields in fields_arg from message_name messages, dump to csv file
# pathname - fit file to extract from
# message_name - name of message to extract, hrv | record
# fields_arg - comma separated list of field names from argument string, e.g. 'time,time2,uvolt'
#
def extract(pathname, message_name, fields_arg):
    fieldnames = fields_arg.split(',')
    fields_str = ''.join(f"-{f}" for f in fieldnames)
    filename = os.path.basename(os.path.splitext(pathname)[0])
    fout_name = f"{filename}-{message_name}-{fields_str}.csv"
    print('%s: ' % (fout_name), file=sys.stderr, end='')
    with open(fout_name, 'w', newline='') as fout:
        csvwriter = csv.DictWriter(fout, fieldnames=fieldnames, extrasaction='ignore') 
        csvwriter.writeheader()
        with fitdecode.FitReader(pathname, error_handling=fitdecode.ErrorHandling.IGNORE) as fit:
            for frame in fit:
                row = {}
                if frame.frame_type == fitdecode.FIT_FRAME_DATA:
                    print('.', file=sys.stderr, end='')
                    if frame.name == message_name:
                        values = { f: [] for f in fieldnames } 
                        fields = [ f.name for f in frame]
                        for i, field in enumerate(frame):
                            if field.name in fieldnames:
                                value = frame.get_value(field.def_num)
                                try:
                                    for v in value:
                                        values[field.name].append(v)
                                except TypeError:
                                    values[field.name].append(value)

                        for i in range(max([len(values[k]) if k in values else 0 for k in values])):
                            row = {k: values[k][i] if i < len(values[k]) else '' for k in values}
                            csvwriter.writerow(row)
    print('', file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description='fitextract', epilog='Extract Hrv or Record data fields to CSV file')
    parser.add_argument('--hrv', type=str, help='Extract Hrv Message fields')
    parser.add_argument('--record', type=str, help='Extract Hrv Message fields')
    parser.add_argument('fitfile', nargs=1,  type=str, help='FIT File')
    args = parser.parse_args()
    for p in args.fitfile:
        if args.hrv is not None:
            extract(p, 'hrv', args.hrv)
        if args.record is not None:
            extract(p, 'record', args.record)

if __name__ == "__main__":
    main()
