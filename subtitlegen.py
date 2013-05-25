#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function, division
import csv
import sys
import re

def partition(begin=None, end=None, n=10, start=0, finish=1):
    """ 
    Returns `n` timestamps that represent a ordered partition,
    time goes from begin to end; distance goes from start to finish.
    """
    ONE_MILLISECOND = Timestamp.from_ms(1)

    delta_t, delta_s = end.to_ms() - begin.to_ms(), finish - start
    d_t, d_s = delta_t // n, delta_s / n
    current_t, current_s = begin.to_ms(), start
    cuts = []
    for i in range(n + 1):
        cuts.append( 
            current_s, 
            Timestamp.from_ms(current_t), 
            Timestamp.from_ms(current_t + d_t - ONE_MILLISECOND) 
        )
        current_t += d_t
        current_s += d_s
    return cuts


class Timestamp(object):
    """ 
    hh:mm:ss,mmm object, that run from 00:00:00,000 to 59:59:59,999
    """
    def __init__(self, value='00:00:00,000'):
        mo = re.match('([0-5][0-9]):([0-5][0-9]):([0-5][0-9])(,([0-9]{3,3}))?', value)
        if not mo:
            raise ValueError('cannot parse "%s" into a Timestamp' % value)
        self.hours = long(mo.group(1) or '00')
        self.minutes = long(mo.group(2) or '00')
        self.seconds = long(mo.group(3) or '00')
        self.milliseconds = long(mo.group(5) or '000')

    @classmethod
    def from_ms(self, milliseconds):
        """ 
        Factory method to create Timestamp from milliseconds.
        """
        ts = Timestamp()
        current = long(milliseconds)
        if current > 215999999: # or current < 0:
            raise ValueError('Between 00:00:00,000 and 59:59:59,999 only.')
        ts.hours = current // (1000 * 60 * 60)
        current -= ts.hours * (1000 * 60 * 60)
        ts.minutes = current // (1000 * 60)
        current -= ts.minutes * (1000 * 60)
        ts.seconds = current // (1000)
        current -= ts.seconds * (1000)
        ts.milliseconds = current
        return ts

    def to_ms(self):
        return (
            long(self.milliseconds) + 
            1000 * long(self.seconds) + 
            1000 * 60 * long(self.minutes) + 
            1000 * 60 * 60 * long(self.hours))

    def __add__(self, other):
        return Timestamp.from_ms(self.to_ms() + other.to_ms())

    def __sub__(self, other):
        return Timestamp.from_ms(self.to_ms() - other.to_ms())

    def __str__(self):
        return '{:02d}:{:02d}:{:02d},{:03d}'.format(
            self.hours, self.minutes, self.seconds, self.milliseconds)

    def __repr__(self):
        return self.__str__()        

ONE_MILLISECOND = Timestamp.from_ms(1)

def main():
    with open('sample.csv') as handle:
        reader = csv.reader(handle)
        rows = [ row for row in reader ]
        for i, row in enumerate(rows[:-1]):
            try:
                begin = Timestamp(rows[i][1])
                end = Timestamp(rows[i + 1][1]) - ONE_MILLISECOND

                # s0 = float(rows[i][0])
                # s1 = float(rows[i + 1][0])
                # sm = s0 + ((s1 - s0) / 2)
                # t0 = Timestamp(rows[i][1])
                # t1 = Timestamp(rows[i + 1][1]) - ONE_MILLISECOND
                # tm = t0 + Timestamp.from_ms((t1 - t0).to_ms() / 2)
                # print(s0, t0, tm)
                # print(sm, tm + ONE_MILLISECOND, t1)
                for s, t in partition(begin=begin, end=end, n=5, 
                        start=long(rows[i][0]), 
                        finish=long(rows[i + 1][0])):
                    print('\t%s %s' % (s, t))
            except ValueError as err:
                print('parse error: {}'.format(err), file=sys.stderr)

    return 0

if __name__ == '__main__':
    sys.exit(main())
