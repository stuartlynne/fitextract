# fitextract
# Thu 16 Feb 2023 07:06:20 PM PST

## Overview

*fitextract* uses *python\_fit\_tool* to parse *Garmin FIT* files to extract *RECORD* and *HRV* data into *CSV* files.

```
usage: fitextract.py [-h] [--hrv] [--record RECORD] [--device_index DEVICE_INDEX] [--expand] [--timestamp] [--no-datestamp] [-V] fitfile
fitextract.py: error: the following arguments are required: fitfile
```

## Options
### --ex
Fields that have multiple values are expanded into multiple lines. See *--hrv*.

### --device\_index=N
FIT files associate the default device with the default workout data. Typically it is the combined data from
multiple sensors, e.g. Heart Rate monitor, Power Meter, etc. This can be specified as device\_index=0 or by not
specifying a device.

### --timestamp
By default the *Record* message *timestamp* field will be converted to a *datestamp*. Using this option
will include the raw timestamp as well.

### -- no-datestamp
By default a *datestamp* from the *timestamp* field will be included. Using this option will prevent that.

### --hrv

Expanded:
```
fitextract.py --hrv -ex 2023-02-12-01-07-35-whiskey.fit
head 2023-02-12-01-07-35-whiskey-hrv--time-ex.csv
time
1.775
0.946
0.964
0.961
0.994
0.388
```

No expanded:
```
fitextract.py --hrv ex 2023-02-12-01-07-35-whiskey.fit
head 2023-02-12-01-07-35-whiskey-hrv--time-ex.csv
time
1.775
0.946
0.964
"[0.961, 0.994]"
0.388
```

### --record all|fields

Dump Record messages. The required option is either *all* or a list of the fields to be dumped. 

Specific devices can be specified using --device\index=N.



