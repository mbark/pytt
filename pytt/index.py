#!/usr/bin/env python
from bitstring import ConstBitStream, BitArray
import logging


log = logging.getLogger('pytt')


# For reference of how the files are structured, see:
# https://github.com/git/git/blob/master/Documentation/technical/index-format.txt
class Index:
    def __init__(self, content):
        # The index file always starts with the entry DIRC, ignore that
        bits = ConstBitStream(content[4:])
        self.version = bits.read(32).int
        self.file_count = bits.read(32).int

        self._parse_entries(bits)

        # These are the last 20 bytes of the file
        # We don't use the bitstream here since git has extensions which
        # can take up an indefinite amount between the last entry and where
        # the checksum is
        self.checksum = BitArray(content[-20:]).hex
        # TODO: extensions should be mentioned here

    def _parse_entries(self, bits):
        self.entries = []

        for i in range(0, self.file_count):
            self.entries.append(Entry(bits))


class Entry:
    STATIC_ENTRY_BYTES = 62

    def __init__(self, bits):
        self.ctime = bits.read('bytes:8').hex()
        self.mtime = bits.read('bytes:8').hex()
        self.device = bits.read('bytes:4').hex()
        self.inode = bits.read('bytes:4').hex()

        bits.pos += 16 # first 16 bit are just 0s
        self.mode_type = bits.read(4).bin
        bits.pos += 3 # 3 unused bytes to throw away
        self.mode_permissions = bits.read(9).oct
        self.uid = bits.read('bytes:4').hex()
        self.gid = bits.read('bytes:4').hex()
        self.file_size = bits.read('bytes:4').hex()
        self.sha1 = bits.read('bytes:20').hex()

        self.assume_valid = bits.read(1).bin
        self.extended_flag = bits.read(1).bin
        self.stage_flag = bits.read(2).int
        self.length = bits.read(12).int
        # Assume there are no extended flags (in case there are they)
        # they will take up 2 bytes of space

        self.name = bits.read('bytes:%s' % self.length).decode()

        padding = (8 - (self.STATIC_ENTRY_BYTES + self.length % 8)) % 8
        bits.bytepos += padding

