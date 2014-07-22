__author__ = 'keckbug'

import cmtools

cDB = cmtools.CyclemeterDB(filename="Meter.db")

for run in cDB.runs:
    print run

print len(cDB.runs)
for run in cDB.runs:
    run.makegpx("{}.gpx".format(run.data['runID']))


