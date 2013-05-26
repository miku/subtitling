#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function, division
import argparse
import csv
import sys
import re

SRT_ITEM = """
{counter}
{begin} --> {end}
{message}"""

class Timerange(object):
    """ Helper object representing an interval.
    """
    def __init__(self, begin=None, end=None):
        if not begin and not end:
            raise ValueError('start and end required')
        self.begin = begin
        self.end = end

    def length(self, unit='milliseconds'):
        millis = (self.end.to_ms() - self.begin.to_ms())
        if unit == 'seconds':
            return millis / 1000
        return millis

    def partition(self, n=10):
        delta = self.length() / n
        begin = self.begin
        parts = []
        for i in range(n):
            end = Timestamp.from_ms(begin.to_ms() + delta - 1)
            parts.append(Timerange(begin=begin, end=end))
            begin = Timestamp.from_ms(begin.to_ms() + delta)
        return parts

    def __str__(self):
        return '<Timerange {0.begin} -- {0.end} [{1:03.3f}s]>'.format(self, self.length('seconds'))

class Timestamp(object):
    """ hh:mm:ss,mmm object, that run from 00:00:00,000 to 59:59:59,999
    """
    def __init__(self, value='00:00:00,000'):
        mo = re.match('([0-5][0-9]):([0-5][0-9]):([0-5][0-9])', value)
        if not mo:
            raise ValueError('cannot parse "%s" into a Timestamp' % value)
        self.minutes = long(mo.group(1) or '00')
        self.seconds = long(mo.group(2) or '00')
        self.milliseconds = long(mo.group(3) or '00')
        self.hours = 0

    @classmethod
    def from_ms(self, milliseconds):
        """ 
        Factory method to create Timestamp from milliseconds.
        """
        ts = Timestamp()
        current = long(milliseconds)
        if current > 215999999: # or current < 0:
            raise ValueError('Between 00:00:00,000 and 59:59:59,999 only.')
        ts.minutes = current // 60000
        current -= ts.minutes * 60000
        ts.seconds = current // 1000
        current -= ts.seconds * 1000
        ts.milliseconds = current
        return ts

    def to_ms(self):
        return (
            long(self.milliseconds) + 
            1000 * long(self.seconds) + 
            1000 * 60 * long(self.minutes))

    def __add__(self, other):
        return Timestamp.from_ms(self.to_ms() + other.to_ms())

    def __sub__(self, other):
        return Timestamp.from_ms(self.to_ms() - other.to_ms())

    # def __str__(self):
    #     return '{:02d}:{:02d}:{:02d},{:03d} [{:02d}]'.format(
    #         self.hours, self.minutes, self.seconds, self.milliseconds, self.to_ms())

    def __str__(self):
        return '{:02d}:{:02d}:{:02d},{:03d}'.format(
            self.hours, self.minutes, self.seconds, self.milliseconds)

    def __repr__(self):
        return self.__str__()        

def render_subtitle_item(counter=None, begin=None, end=None, message=None):
    return SRT_ITEM.format(**locals())

ONE_MILLISECOND = Timestamp.from_ms(1)


def main():

    parser = argparse.ArgumentParser('subtitlegen')
    parser.add_argument('-p', '--partition', metavar='N', type=int, 
        help='partition into N parts')
    parser.add_argument('file', type=str, metavar='FILE', help='input CSV file')
    parser.add_argument('-l', '--long', default=False, 
        action='store_true', help='more info in subtitles')

    args = parser.parse_args()

    with open(args.file) as handle:
        reader = csv.reader(handle)
        rows = [ row for row in reader ]
        counter, distance = 0, 0

        for i, row in enumerate(rows[:-1]):
            try:
                current, nxt = rows[i], rows[i + 1]
                d = current[0] # the current distance
                begin, end = map(Timestamp, [current[1], nxt[1]])
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

                        distance += 1 / (args.partition)
                        counter += 1

                # if we only use the CSV data ...
                else:
                    __end = rng.end - ONE_MILLISECOND
                    if args.long:
                        message = "~ %s m [%s | %s]" % (
                            d, rng.begin, 
                            round(rng.length(unit='seconds')))
                    else:
                        message = "~ %s m" % (distance)
                    print(render_subtitle_item(counter=counter,
                        begin=rng.begin, end=__end,
                        message=message))

                    counter += 1
                    distance = d

            except ValueError as err:
                print('parse error: {}'.format(err), file=sys.stderr)

    return 0

if __name__ == '__main__':
    sys.exit(main())
