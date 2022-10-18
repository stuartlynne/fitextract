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

## fitextract

fitextract is a simple Python script that will extract data fields from Garmin FIT
files and put into CSV files.

This will extract the power and cadence fields from the Record message and put into workout.csv:

```
    fitextract --record 'power, cadence' workout.fit
```

This will allow extraction of data from FIT files, including the developer fields in the Hrv message.


