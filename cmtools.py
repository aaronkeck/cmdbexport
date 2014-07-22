"""
Export and maniupalte Cyclemeter DB files
"""

import sqlite3
from datetime import datetime, timedelta
import gpxpy
import gpxpy.gpx
from bisect import bisect_left

class CyclemeterDB:

    def __init__(self, filename):
        try:
            db = sqlite3.connect(filename)
            db.row_factory = sqlite3.Row
            c = db.cursor()
        except Exception as ex:
            print "Error opening {}".format(filename)
            print ex.message
            print ex.args
            return

        self.runs = []

        c.execute("SELECT * from run")
        cruns = c.fetchall()

        for row in cruns:
            c.execute("SELECT * from coordinate where runID=?", (row['runID'],))
            ccoords = c.fetchall()
            c.execute("SELECT * from altitude where runID=?", (row['runID'],))
            calts = c.fetchall()
            c.execute("SELECT * from stopDetection where runID=?", (row['runID'],))
            cstops = c.fetchall()
            self.runs.append(Run(row, coords=ccoords, alts=calts, stops=cstops))


class Run:

    def __init__(self,data,coords=None, alts=None, stops=None):
        self.data = data
        self.coords = coords
        self.alts = alts
        self.stops = stops

    def __str__(self):
        return "{} - {} - {} coords - {} alts".format(self.data['runID'], self.data['startTime'], len(self.coords), len(self.alts))

    def __unicode__(self):
        return self.__str__()

    def track(self, starttime, endtime):
        return [x for x in self.coords if x['timeOffset'] > starttime and x['timeOffset'] < endtime]

    def makegpx(self, filename):

        gpx = gpxpy.gpx.GPX()
        gpx_track = gpxpy.gpx.GPXTrack()
        gpx.tracks.append(gpx_track)

        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)
        for coord in self.coords:
            coordtime = datetime.strptime(self.data['startTime'], "%Y-%m-%d %H:%M:%S.%f") + timedelta(seconds=coord['timeOffset'])
            #print coordtime
            #print coord['latitude'], coord['longitude'], self.data['startTime'], coord['timeOffset']
            gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(coord['latitude'],coord['longitude'], time=coordtime, elevation=self.find_nearest_altitude(coord['timeOffset'])['altitude']))

        with open(filename, 'w') as fp:
            fp.write(gpx.to_xml())

    def find_nearest_altitude(self, target):
        #print "Target: {}".format(target)
        pos = bisect_left([x['timeOffset'] for x in self.alts], target)
        if pos == 0:
            return self.alts[pos]
        if pos == len(self.alts):
            return self.alts[-1]
        before = self.alts[pos -1]
        after = self.alts[pos]
        if after['timeOffset'] - target < target - before['timeOffset']:
            return after
        else:
            return before
