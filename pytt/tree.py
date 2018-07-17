#!/usr/bin/env python
from bitstring import ConstBitStream, BitArray, Bits
import logging

log = logging.getLogger('pytt')

class Tree:
    def __init__(self, new=False, **kwargs):
        if new:
            self.new(**kwargs)
        else:
            self.from_string(**kwargs)

    def from_string(self, content):
        bits = ConstBitStream(content)
        self.entries = []
        while(bits.pos < bits.length):
            self.entries.append(Entry(new=False, bits=bits))

    def new(self, entries):
        self.entries = entries

    def pack(self):
        bits = BitArray('')
        for entry in self.entries:
            bits.append(Bits(entry.pack()))

        return bits.bytes


class Entry:
    def __init__(self, new=False, **kwargs):
        if new:
            self.new(**kwargs)
        else:
            self.from_bitstring(**kwargs)

    def from_bitstring(self, bits):
        self.mode = _read_till(bits, b' ')
        if(self.mode == b'40000'):
            # pad the mode with a leading 0 to make it the same length as other modes
            self.mode = Bits().join([b'0', self.mode]).bytes
            self.object_type = 'tree'
        else:
            self.object_type = 'blob'

        self.name = _read_till(bits, b'\0').decode()
        self.sha1 = bits.read('bytes:20').hex()

    def new(self, mode_type, mode_permissions, sha, name):
        self.mode = Bits(bytes=(bin(mode_type)[2:-1] + oct(mode_permissions)[2:]).encode()).bytes
        self.name = name
        self.sha1 = sha

    def pack(self):
        bits = BitArray('')
        bits.append(Bits(bytes=self.mode))
        bits.append(Bits(b' '))
        bits.append(Bits(self.name.encode()))
        bits.append(Bits(b'\0'))
        bits.append(Bits(hex=self.sha1))

        log.debug(bits)

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
