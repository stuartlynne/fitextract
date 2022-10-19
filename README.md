# fitextract
# Mon 17 Oct 2022 02:38:25 PM PDT

## Overview

This project documents several Developer Fields being used in Garmin FIT files to
support various objectives:

- DFA Alpha1
- multiple heart rate and power sensors
- MO2 and VO2 sensors
- ECG data

See [README-FIT](./README-FIT.md) for more information.

It also contains example python scripts to extract field data from *Record* and *Hrv* messages, 
implemented using the *fit\_tool*, *fitdecode* and *fitparse* Python libraries.

## fitextract

The three versions of fitextract are simple Python scripts that will extract data fields from Garmin FIT
files and put into CSV files.

This will extract the power and cadence fields from the Record message and put into workout.csv:

```
    fitextract --record 'power, cadence' workout.fit
```

This will allow extraction of data from FIT files, including the developer fields in the Hrv message.

There are three versions provided:

- fittool\_extract.py
- fitdecode\_extract.py
- fitparse\_extract.py

## fit\_tool

*fit\_tool* is a new Python library for reading and writing Garmin FIT files, implemented and published
by Stages Cycling.

(Github archive for FitTool)[https://bitbucket.org/stagescycling/python\_fit\_tool.git]

## fitdecode

*fitdecode* is a new Python library for parsing and decoding Garmin FIT files.

(Github archive for FitDecode)[https://github.com/polyvertex/fitdecode.git] 

## fitparse

*fitparse* is the original Python library for parsing Garmin FIT files.

(Github archive for FitParse)[https://github.com/dtcooper/python-fitparse.git]
