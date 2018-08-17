#!/usr/bin/env python
from bitstring import ConstBitStream, BitArray, Bits
from functools import reduce
import logging

log = logging.getLogger('pytt')


class Tree:
    def __init__(self, entries=[]):
        self.entries = entries

    @classmethod
    def from_string(cls, content):
        bits = ConstBitStream(content)
        entries = []
        while(bits.pos < bits.length):
            entries.append(Tree.Entry.from_bitstring(bits))

        return Tree(entries)

    def pack(self):
        bits = BitArray(b'')
        for entry in self.entries:
            bits.append(Bits(entry.pack()))

        return bits.bytes

    class Entry:
        def __init__(self, name, sha, mode=None, mode_type=None, mode_permissions=None):
            if mode_type and mode_permissions:
                self.mode = Bits(
                    bytes=(bin(mode_type)[2:-1] + oct(mode_permissions)[2:]).encode()).bytes
            else:
                self.mode = mode
            self.name = name
            self.sha1 = sha

        @classmethod
        def from_bitstring(cls, bits):
            mode = _read_till(bits, b' ')
            name = _read_till(bits, b'\0')
            sha = bits.read('bytes:20').hex()

            return Tree.Entry(name, sha, mode=mode)

        def pack(self):
            bits = BitArray('')
            bits.append(Bits(bytes=self.mode))
            bits.append(Bits(b' '))
            bits.append(Bits(self.name.encode()))
            bits.append(Bits(b'\0'))
            bits.append(Bits(hex=self.sha1))

            log.debug(bits)

            return bits.bytes


class Person:
    def __init__(self, name=b'Foo Bar', email=b'foo.bar@email.com', date_s=1531840055, date_timezone=b'+0200'):
        self.name = name
        self.email = email
        self.date_s = date_s
        self.date_timezone = date_timezone

    @classmethod
    def from_string(cls, line, prefix):
        line.bytepos += len('\n%s ' % prefix)
        splits = list(line.split(b' ', start=line.pos, bytealigned=True))
        date_timezone = splits[-1][8:].bytes
        date_s = splits[-2][8:].bytes
        email = splits[-3][8:].bytes
        name = reduce(
            (lambda sum, next: sum + next.bytes), splits[:-3], b'')

        return Person(name, email, date_s, date_timezone)

    def __str__(self):
        return b' '.join([self.name, self.email, str(self.date_s).encode(), self.date_timezone]).decode()


class Commit:
    def __init__(self, tree, parents, author, comitter, message):
        self.tree = tree
        self.author = author
        self.committer = comitter
        self.message = message
        self.parents = parents

    @classmethod
    def create(cls, tree, message, parent=None):
        author = Person()
        commiter = author
        parents = [] if parent is None else [parent.encode()]
        return Commit(tree.encode(), parents, author, commiter, message.encode())

    @classmethod
    def from_string(cls, content):
        bits = ConstBitStream(content)
        lines = list(bits.split(b'\n', bytealigned=True))

        lines[0].bytepos += len('tree ')
        tree = lines[0].read('bytes:40')

        index = 1
        parents = []
        while(lines[index].startswith(b'\nparent')):
            lines[index].bytepos += len('\nparent ')
            parents.append(lines[index].read('bytes:40'))
            index += 1

        author = Person.from_string(lines[index], 'author')
        committer = Person.from_string(lines[index+1], 'committer')

        # ignore prefix \n
        message = lines[index+3][8:].bytes

        return Commit(tree, parents, author, committer, message)

    def pack(self):
        bits = BitArray('')
        bits.append(Bits(bytes=b'tree %s\n' % self.tree))

        for parent in self.parents:
            bits.append(Bits(bytes=b'parent %s\n' % parent))

        bits.append(Bits(bytes=b'author %s\n' % str(self.author).encode()))
        bits.append(Bits(bytes=b'committer %s\n' %
                         str(self.committer).encode()))
        bits.append(Bits(bytes=b'\n%s' % self.message))

        return bits.bytes


def _read_till(bits, delim):
    start_pos = bits.pos

    found_pos = bits.findall(delim, start=bits.pos, bytealigned=True)
    next_pos = int(list(found_pos)[0] / 8)

    bits.pos = start_pos
    value = bits.read('bytes:%d' % (next_pos - bits.bytepos))

    # move past the found delimiter
    bits.bytepos += 1

    return value