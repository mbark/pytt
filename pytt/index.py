#!/usr/bin/env python
from bitstring import ConstBitStream, BitArray, Bits
from collections import namedtuple
import logging
import os
import struct
import math


log = logging.getLogger('pytt')


# For reference of how the files are structured, see:
# https://github.com/git/git/blob/master/Documentation/technical/index-format.txt
class Index:
    FMT = '>4sii'

    def __init__(self, content):
        size = struct.calcsize(self.FMT)
        _, self.version, self.file_count = _unpack_slice(
            self.FMT, content)

        self.entries = []
        offset = size
        for i in range(0, self.file_count):
            entry = Entry(new=False, content=content, offset=offset)
            self.entries.append(entry)
            offset += entry.size

        # The last 20 bytes are always a checksum
        self.checksum = ConstBitStream(content[-20:]).hex

        # TODO: extensions should be mentioned here


class Entry:
    ENTRY_FMT = '>iiiiii2x2siii20s2s'
    
    def __init__(self, new=False, **kwargs):
        if new:
            self.new(**kwargs)
        else:
            self.from_string(**kwargs)
    
    def from_string(self, content, offset):
        unpacked = _unpack_slice(self.ENTRY_FMT, content, offset)

        StaticEntry = namedtuple(
            'StaticEntry', 'ctime ctime_ns mtime mtime_ns device inode mode uid gid file_size sha1 flags')
        static = StaticEntry._make(unpacked)

        self.ctime = static.ctime
        self.ctime_ns = static.ctime_ns
        self.mtime = static.mtime
        self.mtime_ns = static.mtime_ns

        log.debug('ctime: %s, ctime_ns: %s, mtime: %s, mtime_ns: %s', static.ctime, static.ctime_ns, static.mtime, static.mtime_ns)

        self.device = static.device
        self.inode = static.inode

        log.debug('device: %s, inode: %s', self.device, self.inode)

        self.mode = static.mode
        mode = ConstBitStream(static.mode)
        self.mode_type = mode.read(4).uint
        mode.pos += 3  # 3 unused bytes to throw away
        self.mode_permissions = mode.read(9).uint
        
        log.debug('mode_type: %s, mode_permissions: %s', self.mode_type, self.mode_permissions)

        self.uid = static.uid
        self.gid = static.gid
        self.file_size = static.file_size
        self.sha1 = ConstBitStream(static.sha1).hex

        log.debug('sha1: %s', self.sha1)

        flags = ConstBitStream(static.flags)
        self.assume_valid = flags.read(1).int
        self.extended_flag = flags.read(1).int
        self.stage_flag = flags.read(2).int
        self.length = flags.read(12).int
        
        log.debug('stage_flag: %s', self.stage_flag)

        static_size = struct.calcsize(self.ENTRY_FMT)

        self.name = _unpack_slice(
            '%ss' % self.length, content, offset+static_size)[0].decode()
        padding = (8 - (static_size + self.length % 8)) % 8

        self.size = static_size + self.length + padding

    def new(self, mode, sha, filename):
        def split_time(time):
            frac = math.modf(stat.st_ctime)
            return (int(frac[1]), int(frac[0]*1000*1000*1000))

        stat = os.stat(filename)
        self.ctime, self.ctime_ns = split_time(stat.st_ctime)
        self.mtime, self.mtime_ns = split_time(stat.st_mtime)
        self.device = stat.st_dev
        # the inode can be too large to pack so we just take the first 4 bytes and save them
        self.inode = struct.unpack('i', struct.pack('l', stat.st_ino)[:4])[0]
        
        self.mode_type = int('%s0' % mode[:3], 2)
        self.mode_permissions = int(mode[3:], 8)
        
        self.uid = stat.st_uid
        self.gid = stat.st_gid
        self.file_size = stat.st_size
        self.sha1 = sha

        # We are a bit lazy and cheat with these flags by assuming they are all 0
        self.assume_valid = 0
        self.extended_flag = 0
        self.stage_flag = 0
        self.length = len(filename)
        
        self.name = filename
    
    def pack(self):
        mode_b = BitArray('')
        mode_b.append(Bits(uint=self.mode_type, length=4))
        mode_b.append(Bits(uint=0, length=3))
        mode_b.append(Bits(uint=self.mode_permissions, length=9))
        log.debug(len(mode_b))
        
        log.debug(mode_b.bytes)

        sha1 = bytearray.fromhex(self.sha1)

        flags = BitArray('')
        flags.append(Bits(uint=self.assume_valid, length=1))
        flags.append(Bits(uint=self.extended_flag, length=1))
        flags.append(Bits(uint=self.stage_flag, length=2))
        flags.append(Bits(uint=len(self.name), length=12))
        
        fmt = '%s%ds' % (self.ENTRY_FMT, len(self.name))
        padding = (8 - (struct.calcsize(fmt) % 8)) % 8
        fmt = '%s%dx' % (fmt, padding)
        packed = struct.pack(fmt, self.ctime, self.ctime_ns, self.mtime, self.mtime_ns, self.device, self.inode, mode_b.bytes, self.uid, self.gid, self.file_size, sha1, flags.bytes, self.name.encode())

        log.debug(packed)
        return packed


def _unpack_slice(fmt, content, offset=0):
    size = struct.calcsize(fmt)
    return struct.unpack(fmt, content[offset:offset+size])
