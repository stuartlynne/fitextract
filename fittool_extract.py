#!/usr/bin/env python3
# vim: shiftwidth=4 tabstop=4 expandtab textwidth=0

import os
import sys
import csv
import argparse
import itertools

from fit_tool.data_message import DataMessage
from fit_tool.fit_file import FitFile

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
        fit_file = FitFile.from_file(pathname)
        for i, record in enumerate(fit_file.records):
            if isinstance(record.message, DataMessage):
                print('.', file=sys.stderr, end='')
                if record.message.NAME == message_name:
                    values = { f: [] for f in fieldnames } 
                    for f in itertools.chain(record.message.fields, record.message.developer_fields):
                        if f.name in fieldnames:
                            try:
                                for v in f.get_values():
                                    values[f.name].append(v)
                            except KeyError:
                                values[f.name].append(f.get_value())

                    for j in range(max([len(values[k]) if k in values else 0 for k in values])):
                        row = {k: values[k][j] if len(values[k]) > j else '' for k in values}
                        if csvwriter:
                            csvwriter.writerow(row)
    print('', file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description='fitextract', epilog='Extract Hrv or Record data fields to CSV file')
    parser.add_argument('--hrv', type=str, help='Extract Hrv Message fields')
    parser.add_argument('--record', type=str, help='Extract Hrv Message fields')
    parser.add_argument('fitfile', nargs=1,  type=str, help='FIT File')
    args = parser.parse_args()

    # iterate across files to extract from, extract hrv and record messages separately
    for p in args.fitfile:
        if args.hrv is not None:
            extract(p, 'hrv', args.hrv)
        if args.record is not None:
            extract(p, 'record', args.record)

if __name__ == "__main__":
    main()
