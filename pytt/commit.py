#!/usr/bin/env python
from bitstring import ConstBitStream, BitArray, Bits
from functools import reduce
import logging

log = logging.getLogger('pytt')


class Commit:
    def __init__(self, new=False, **kwargs):
        if new:
            self.new(**kwargs)
        else:
            self.from_string(**kwargs)

    def from_string(self, content):
        bits = ConstBitStream(content)
        lines = list(bits.split(b'\n', bytealigned=True))

        lines[0].bytepos += len('tree ')
        self.tree = lines[0].read('bytes:40')

        # TODO: we can optionally specify one or several parents

        self.author = self._read_name_line(lines[1], 'author')
        self.committer = self._read_name_line(lines[2], 'committer')

        # ignore prefix \n
        self.message = lines[4][8:].bytes
        log.debug(self.message)

    def _read_name_line(self, line, prefix):
        line.bytepos += len('\n%s ' % prefix)
        splits = list(line.split(b' ', start=line.pos, bytealigned=True))
        date_timezone = splits[-1][8:].bytes
        date_s = splits[-2][8:].bytes
        email = splits[-3][8:].bytes
        name = reduce((lambda sum, next: sum + next.bytes), splits[:-3], b'')

        return [name, email, date_s, date_timezone]

    def new(self):
        pass

    def pack(self):
        pass
