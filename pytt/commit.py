#!/usr/bin/env python
from bitstring import ConstBitStream, BitArray, Bits
from functools import reduce
import time
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

        index = 1
        self.parents = []
        while(lines[index].startswith(b'\nparent')):
            lines[index].bytepos += len('\nparent ')
            self.parents.append(lines[index].read('bytes:40'))
            index += 1

        self.author = Person(line=lines[index], prefix='author')
        self.committer = Person(line=lines[index+1], prefix='committer')

        # ignore prefix \n
        self.message = lines[index+3][8:].bytes
        log.debug(self.message)

    def new(self, tree, message, parent=None):
        self.tree = tree.encode()
        self.message = message.encode()
        self.parents = []
        if parent:
            self.parents.append(parent.encode())
        self.author = DEFAULT_PERSON
        self.committer = DEFAULT_PERSON

    def pack(self):
        bits = BitArray('')
        bits.append(Bits(bytes=b'tree %s\n' % self.tree))

        for parent in self.parents:
            bits.append(Bits(bytes=b'parent %s\n' % parent))

        bits.append(Bits(bytes=b'author %s\n' % str(self.author).encode()))
        bits.append(Bits(bytes=b'committer %s\n' % str(self.committer).encode()))
        bits.append(Bits(bytes=b'\n%s' % self.message))

        return bits.bytes


class Person:
    def __init__(self, new=False, **kwargs):
        if new:
            self.new(**kwargs)
        else:
            self.from_string(**kwargs)

    def from_string(self, line, prefix):
        line.bytepos += len('\n%s ' % prefix)
        splits = list(line.split(b' ', start=line.pos, bytealigned=True))
        self.date_timezone = splits[-1][8:].bytes
        self.date_s = splits[-2][8:].bytes
        self.email = splits[-3][8:].bytes
        self.name = reduce((lambda sum, next: sum + next.bytes), splits[:-3], b'')

    def new(self, name, email, date_s, date_timezone):
        self.name = name.encode()
        self.email = email.encode()
        self.date_s = date_s
        self.date_timezone = date_timezone.encode()

    def __str__(self):
        return b' '.join([self.name, self.email, str(self.date_s).encode(), self.date_timezone]).decode()


DEFAULT_PERSON = Person(new=True, name='Foo Bar', email='foo.bar@email.com', date_s=1531840055, date_timezone='+0200')
