#!/usr/bin/env python
# coding: utf-8

"""

`subtitlegen` creates [SRTs](http://en.wikipedia.org/wiki/SubRip) from 
[CSVs](http://en.wikipedia.org/wiki/Comma-separated_values).

> SRT is perhaps the most basic of all subtitle formats. 
See: http://www.matroska.org/technical/specs/subtitles/srt.html

1. Create the **subtitles from csv** via `subtitlegen.py`:

        $ python subtitlegen.py --long sample.csv > sample.srt

    The expected CSV format is as follows (note that the time format is 
    `MM:SS:Milliseconds`, although full milliseconds would need three digits):

        $ cat sample.csv
        0,34:39:00
        1,34:52:00
        2,35:01:00
        3,35:55:00
        ...

    The resulting srt looks like 
    (the time format here is `HH:MM:SS,milliseconds`):

        $ cat sample.srt
        0
        00:34:39,000 --> 00:34:51,999
        ~ 0 m [00:34:39,000 | 13.0]

        1
        00:34:52,000 --> 00:35:00,999
        ~ 1 m [00:34:52,000 | 9.0]

        2
        00:35:01,000 --> 00:35:54,999
        ~ 2 m [00:35:01,000 | 54.0]

        3
        00:35:55,000 --> 00:36:11,999
        ~ 3 m [00:35:55,000 | 17.0]

        ...

"""

from __future__ import print_function, division
import argparse
import csv
import sys
import re

SRT_ITEM = """
{counter}
{begin} --> {end}
{message}"""


def render_subtitle_item(counter=None, begin=None, end=None, message=None):
    """ 
    Helper to render one subtitle item.
    """
    return SRT_ITEM.format(**locals())


class Timerange(object):
    """ 
    Helper object representing an interval between two Timestamps.
    """
    def __init__(self, begin=None, end=None):
        if not begin and not end:
            raise ValueError('start and end required')
        self.begin = begin
        self.end = end

    def __len__(self):
        """ 
        Return the length of this range as seconds or milliseconds. 
        """
        return self.end.to_ms() - self.begin.to_ms()

    def length(self, unit='milliseconds'):
        if unit == 'seconds':
            return len(self) / 1000
        return len(self)  

    def partition(self, n=10):
        """ 
        Partition the range into `n` pieces. Generates Timeranges. 
        """
        delta = len(self) / n
        begin = self.begin
        for _ in range(n):
            end = Timestamp.from_ms(begin.to_ms() + delta - 1)
            yield Timerange(begin=begin, end=end)
            begin = Timestamp.from_ms(begin.to_ms() + delta)

    def __str__(self):
        return '<Timerange {0.begin} -- {0.end} [{1:03.3f}s]>'.format(
            self, self.length('seconds'))

    def __repr__(self):
        return self.__str__()

class Timestamp(object):
    """ 
    Timestamp object, initialization format: mm:ss:ll (where ll = milliseconds)
    corresponds to values found in CSV. To create a Timestamp from milliseconds,
    see: `Timestamp.from_ms(milliseconds)` factory.
    """
    def __init__(self, value='00:00:00'):
        mo = re.match('([0-5][0-9]):([0-5][0-9]):([0-5][0-9])', value)
        if not mo:
            raise ValueError('cannot parse "%s" into a Timestamp' % value)
        self.minutes = long(mo.group(1)) or 0
        self.seconds = long(mo.group(2)) or 0
        self.milliseconds = long(mo.group(3)) or 0
        self.hours = 0

    @classmethod
    def from_ms(cls, milliseconds):
        """
        Factory method to create Timestamp from milliseconds.
        """
        ts = Timestamp()
        current = long(milliseconds)
        if current > 215999999:
            raise ValueError('Between 00:00:00,000 and 59:59:59,999 only.')
        ts.hours = current // 3600000
        current -= ts.hours * 3600000
        ts.minutes = current // 60000
        current -= ts.minutes * 60000
        ts.seconds = current // 1000
        current -= ts.seconds * 1000
        ts.milliseconds = current
        return ts

    def to_ms(self):
        """
        Convert timestamp into milliseconds. 
        """
        return (
            self.milliseconds +
            1000 * self.seconds +
            1000 * 60 * self.minutes +
            1000 * 60 * 60 * self.hours)

    def __add__(self, other):
        if isinstance(other, (int, long)):
            return Timestamp.from_ms(self.to_ms() + other)
        if isinstance(other, Timestamp):
            return Timestamp.from_ms(self.to_ms() + other.to_ms())
        raise ValueError('can only add Timestamp or int (interpreted as ms)')

    def __sub__(self, other):
        if isinstance(other, (int, long)):
            return Timestamp.from_ms(self.to_ms() - other)
        if isinstance(other, Timestamp):
            return Timestamp.from_ms(self.to_ms() - other.to_ms())
        raise ValueError('can only subtract Timestamp or int (interpreted as ms)')

    def __str__(self):
        return '{:02d}:{:02d}:{:02d},{:03d}'.format(
            self.hours, self.minutes, self.seconds, self.milliseconds)

    def __repr__(self):
        return self.__str__()

ONE_MILLISECOND = Timestamp.from_ms(1)


def main():
    """ 
    Parse and go.
    """
    parser = argparse.ArgumentParser('subtitlegen')
    parser.add_argument('-p', '--partition', metavar='N', type=int,
                        help='partition into N parts')
    parser.add_argument('file', type=str, metavar='FILE', help='input CSV file')
    parser.add_argument('-l', '--long', default=False,
                        action='store_true', help='more info in subtitles')

    args = parser.parse_args()

    with open(args.file) as handle:
        rows = [row for row in csv.reader(handle)]
        counter, distance = 0, 0

        for i, _ in enumerate(rows[:-1]):
            try:
                current, nxt = rows[i], rows[i + 1]
                begin, end = [Timestamp(s) for s in [current[1], nxt[1]]]
                rng = Timerange(begin=begin, end=end)

                # if we want smaller intervals ...
                if args.partition:
                    for subrange in rng.partition(n=args.partition):
                        if args.long:
                            message = "~ %s m [%s | %s]" % (
                                distance, subrange.begin,
                                round(subrange.length(unit='seconds')))
                        else:
                            message = "~ %s m" % (distance)
                        print(render_subtitle_item(counter=counter,
                              begin=subrange.begin, end=subrange.end,
                              message=message))

                        distance += (
                            (float(nxt[0]) - float(current[0])) / 
                            (args.partition))
                        counter += 1

                # if we only use the CSV data ...
                else:
                    distance = current[0]    # the current distance
                    if args.long:
                        message = "~ %s m [%s | %s]" % (
                            distance, rng.begin,
                            round(rng.length(unit='seconds')))
                    else:
                        message = "~ %s m" % (distance)
                    print(render_subtitle_item(counter=counter,
                          begin=rng.begin, end=rng.end - ONE_MILLISECOND,
                          message=message))

                    counter += 1

            except ValueError as err:
                print('parse error: {}: file={}, line={}, current={}, next={}'.format(
                       err, args.file, i + 1, current, nxt), file=sys.stderr)

    return 0

if __name__ == '__main__':
    sys.exit(main())
