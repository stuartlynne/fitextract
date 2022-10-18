# FIT File Developer Fields for HRV and multiple sensors
## Overview

This describe the developer fields used to add additional data to FIT data files:

- DFA Alpha1
- Respiration Rate
- Second Heart Rate Monitor
- ECG data
- Second Power Meter or FEC

Generally these are intended to facilitate:

- use of DFA A1, Respiration Rate and ECG data in post-workout analysis
- dual-power recording

Dual-power recording allows for post-workout comparison of multiple power sensors
including FE-C trainers.


## DFA Alpha1

DFA Alpha1 developer fields are added to the Record message:

- Alpha1 - DFA A1 value for preceding period (typically 120s)
- Artifacts - the number of artifacts encountered in the preceding DFA A1 period
- Corrections - the number of corrections in the current sample (typically 1s)

*Corrections* are the actual number of corrected RR intervals in the current Record sample (e.g. preceding second).

*Artifacts* are the total number of corrected RR intervals in the current DFA A1 period (typically 120 seconds).


## Respiration Rate

This is the respiration rate for the current sample.

- RespirationRate


## Second Heart Rate Monitor

There are three types of data being recorded:

- heart beat rate at 1 Hz
- RR interval data as received (between .5 and 5 Hz)

These fields are added to the Record message:

- heart\_rate\_2

These fields are added to the Hrv message:

- time\_2 - the RR interval data 


## ECG Data 

Some heart rate monitors (e.g. Polar H10) can provide ECG data. Saving this to the FIT
file with timestamps will allow post event comparison to other workout statistics, 
e.g. DFA A1, power, cadence, heart rate.

The Hrv message can be used to save this data. Typically one message will be sent with the
data from the heart rate monitor as received. Currently that appears to be 70 uvolt values
at a time. Periodically (typically when event, session or lap messages are sent) the timestamp
field will be added to help with synchronizing the ECG data to the data in the Record messages.

These fields are added to the Hrv message:

- uVolts (aka ECG) data 130 Hz, typically 70 values per message
- ts - timestamp, typically sent when event, lap or session messages sent

## Power and FEC Data

These add additional fields that duplicate the data fields already in the Record message
to carry data for an additional sensor:

- power\_2
- power\_fec
- cadence\_2
- cadence\_fec

The intent of these fields is to facilitate "dual-power" recording. It may be necessary
to add additional fields as appropriate as needed. 


## Hrv Message 

The Hrv message as defined in the FIT SDK has a single field, 'time'. Adding additional developer fields to
Hrv is allowed and works well. 

Fields added:

- time\_2 - rr interval data from a second heart rate monitor
- uvolts - ECG data from (for example) a Polar H10
- ts - a time stamp that can be used to synchronize ECG data to the record messages

The *time*, *time\2* and *uvolt* fields are sent as arrays of values. The suggested use is to periodically
send the accumulated data for *time* and *time2* together. 

ECG datasets are larger and will usually be
sent as received when received (typically for Polar H10, 70 samples every 70/130 seconds.) 

The *ts* time stamp should be sent when ECG data starts, and when major events happen such
as sending an Event, Session or Lap message.

## Hrv Message Issues
There is a caveat that while Fit file parsers should have little problem parsing the data correctly,
some applications may incorrectly assume that all data in the Hrv message is 'time' without
looking at the field names.

For example, this code using the python fitparse library finds all of the Hrv data but 
does not correctly check for the field name:

'''
for record in fit\_file.get\_messages('hrv'):
    for record\_data in record:
        for RR\_interval in record\_data.value:
            if RR\_interval is not None:
                print('%.0f,' % (RR\_interval*1000.), file=sys.stdout)
'''

Adding a single line to check the field name is 'time' is all that is required to 
make this work correctly.

'''
for record in fit\_file.get\_messages('hrv'):
    for record\_data in record:
        if record\_data.name == 'time': # check that we have a 'time' field 
            for RR\_interval in record\_data.value:
                if RR\_interval is not None:
                    print('%.0f,' % (RR\_interval*1000.), file=sys.stdout)
'''


