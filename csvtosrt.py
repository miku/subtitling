#!/usr/bin/env python
# coding: utf-8

"""

Example how to convert data from a CSV to a subtitles file using
[pysrt](https://github.com/byroot/pysrt).

CSV looks like this:

    $ cat sample.csv
    0,34:39:00
    1,34:52:00
    2,35:01:00
    3,35:55:00
    4,36:12:00
    5,36:13:00
    6,36:56:00
    7,37:06:00
    8,37:16:00
    9,37:26:00
    10,37:40:00
    11,37:45:00
    12,37:53:00
    13,38:01:00
    14,38:10:00
    15,38:17:00
    16,38:25:00
    17,38:34:00
    18,38:40:00

To preview the srt on a movie:

    $ mplayer -sub sample.srt galactic_timelapse.avi

To merge it, see: http://www.patrickmin.com/linux/tip.php?name=subtitles

"""

import csv
import pysrt
import datetime
from collections import namedtuple

def strfdelta(tdelta, fmt):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)

def seconds_to_hmsm(seconds):
    """ 
    returns a 3-tuple (hours, minutes, seconds) 
    """
    d = datetime.datetime(1, 1, 1) + datetime.timedelta(seconds=int(seconds))
    TimeFields = namedtuple('TimeFields', ['hours', 'minutes', 'seconds'])
    return TimeFields(hours=d.hour, minutes=d.minute, seconds=d.second)

if __name__ == '__main__':
    with open('sample.csv') as csvfile:
        reader = csv.reader(csvfile)
        lines = [ row for row in reader ]
        # items = []
        start = datetime.datetime.strptime(lines[0][1], "%M:%S:%f")
        deltas = []
        for i, line in enumerate(lines[:-1]):
            # print(lines[i], lines[i + 1])
            try:
                t0 = datetime.datetime.strptime(lines[i][1], "%M:%S:%f")
                t1 = datetime.datetime.strptime(lines[i + 1][1], "%M:%S:%f")
                # print(t0, t1)
                delta = t0 - start
                # adjusted = start + delta
                # print(delta)
                deltas.append(delta)
            except ValueError:
                pass
            # timefields = seconds_to_hmsm(i)
            # start = pysrt.SubRipTime(
            #     hours=timefields.hours, 
            #    minutes=timefields.minutes, 
            #    seconds=timefields.seconds, milliseconds=0)
            # end = pysrt.SubRipTime(
            #     hours=timefields.hours, 
            #     minutes=timefields.minutes, 
            #     seconds=timefields.seconds, milliseconds=999)
            # item = pysrt.SubRipItem(i, start, end, 
            #     '%s [%s]' % (line[0], line[1]))
            # items.append(item)

        milli = datetime.timedelta(0, 0, 1000) # 1000 microseconds

        with open("sample.srt", "w") as handle:
            for i, d in enumerate(deltas[:-1]):
            # print(i, deltas[i], deltas[i + 1])
            # print("%s m [%s-%s]" % (i, deltas[i], deltas[i + 1]))
                start = strfdelta(deltas[i], "00:0{minutes}:{seconds},000")
                stop = strfdelta(deltas[i + 1] - milli, "00:0{minutes}:{seconds},000")
                handle.write("%s\n" % i)
                handle.write("%s --> %s\n" % (start, stop))
                handle.write("%sm [%s - %s]\n\n" % (i, start, stop))
            # print("%s m [%s-%s]" % (i, start, stop)
            
        # srt = pysrt.SubRipFile(items=items, path='sample.srt')
        # srt.save()
