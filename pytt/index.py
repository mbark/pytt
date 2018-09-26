#!/usr/bin/env python
from __future__ import annotations

import logging
import math
import os
import struct
from collections import namedtuple
from typing import List

from bitstring import BitArray, Bits, ConstBitStream

log = logging.getLogger("pytt")


# For reference of how the files are structured, see:
# https://github.com/git/git/blob/master/Documentation/technical/index-format.txt
class Index:
    """The index describes the staging area, i.e. the area which will eventually
    be constructed into a tree (and typically a commit describing that tree).

    The index contains some metadata as well as a list of all files in the
    staging area. The index doesn't contain any directories -- only files.
    """

    FMT = ">4sii"

    def __init__(self, content: bytes) -> None:
        size = struct.calcsize(self.FMT)
        self.header, self.version, self.file_count = _unpack_slice(self.FMT, content)

        self.entries = {}
        offset = size
        for _ in range(0, self.file_count):
            entry = Index.Entry(new=False, content=content, offset=offset)
            self.entries[entry.name] = entry
            offset += entry.size

        # Extensions are ignored

        # The last 20 bytes are always a checksum
        self.checksum = ConstBitStream(content[-20:])

    def append(self, new_entry: Index.Entry) -> None:
        self.entries[new_entry.name] = new_entry

    def pack(self) -> bytes:
        packed = BitArray("")

        packed_index = struct.pack(
            self.FMT, self.header, self.version, len(self.entries)
        )
        packed.append(packed_index)

        for _, entry in sorted(self.entries.items()):
            packed.append(entry.pack())

        packed.append(self.checksum)
        return packed.bytes

    class Entry:
        """An entry describes a single entry in the index.

        The entry contains information about the file that is relevant to git,
        i.e. the mode, modification time etc.

        Examples
        --------
        A new Tree Entry can be constructed by passing new=True to the
        constructor as well as the parameters for the new method.

        >>> Index.Entry.create_new(mode, sha, filename) 
        """

        ENTRY_FMT = ">iiiiii2x2siii20s2s"

        def __init__(self, new=False, **kwargs) -> None:
            if new:
                self.new(**kwargs)
            else:
                self.unpack(**kwargs)

        def __eq__(self, other) -> bool:
            return self.name == other.name

        def __hash__(self) -> str:
            return hash(self.name)

        def __str__(self) -> str:
            # why the -1? Well the mode type is 1000, 1010 or 1100 and
            # permissions 0755 or 0644 so git decides to cut a 0 when
            # concatenating them.
            mode = "%s%s" % (bin(self.mode_type)[2:-1], oct(self.mode_permissions)[2:])
            return "%s %s %s\t%s" % (mode, self.sha, self.stage_flag, self.name)

        @classmethod
        def create_new(cls, mode: str, sha: str, filename: str) -> Index.Entry:
            """Create a new Tree Entry from the given mode, sha and filename."""
            return Index.Entry(new=True, mode=mode, sha=sha, filename=filename)

        def unpack(self, content: bytes, offset: int) -> None:
            unpacked = _unpack_slice(self.ENTRY_FMT, content, offset)

            StaticEntry = namedtuple(
                "StaticEntry",
                "ctime ctime_ns mtime mtime_ns device inode mode uid gid file_size sha flags",
            )
            static = StaticEntry._make(unpacked)

            self.ctime = static.ctime
            self.ctime_ns = static.ctime_ns
            self.mtime = static.mtime
            self.mtime_ns = static.mtime_ns

            log.debug(
                "ctime: %s, ctime_ns: %s, mtime: %s, mtime_ns: %s",
                static.ctime,
                static.ctime_ns,
                static.mtime,
                static.mtime_ns,
            )

            self.device = static.device
            self.inode = static.inode

            log.debug("device: %s, inode: %s", self.device, self.inode)

            self.mode = static.mode
            mode = ConstBitStream(static.mode)
            self.mode_type = mode.read(4).uint
            mode.pos += 3  # 3 unused bytes to throw away
            self.mode_permissions = mode.read(9).uint

            log.debug(
                "mode_type: %s, mode_permissions: %s",
                self.mode_type,
                self.mode_permissions,
            )

            self.uid = static.uid
            self.gid = static.gid
            self.file_size = static.file_size
            self.sha = ConstBitStream(static.sha).hex

            log.debug("sha: %s", self.sha)

            flags = ConstBitStream(static.flags)
            self.assume_valid = flags.read(1).int
            self.extended_flag = flags.read(1).int
            self.stage_flag = flags.read(2).int
            self.length = flags.read(12).int

            log.debug("stage_flag: %s", self.stage_flag)
            log.debug("length: %s" % self.length)

            static_size = struct.calcsize(self.ENTRY_FMT)

            self.name = _unpack_slice(
                "%ss" % self.length, content, offset + static_size
            )[0].decode()

            padding = 8 - (static_size + self.length) % 8
            self.size = static_size + self.length + padding

        def new(self, mode: str, sha: str, filename: str) -> None:
            def split_time(time):
                frac = math.modf(stat.st_ctime)
                return (int(frac[1]), int(frac[0] * 1000 * 1000 * 1000))

            if not os.path.isfile(filename):
                with open(filename, "w"):
                    pass

            stat = os.stat(filename)
            self.ctime, self.ctime_ns = split_time(stat.st_ctime)
            self.mtime, self.mtime_ns = split_time(stat.st_mtime)
            self.device = stat.st_dev
            # the inode can be too large to pack so we just take the first 4 bytes and save them
            self.inode = struct.unpack("i", struct.pack("l", stat.st_ino)[:4])[0]

            self.mode_type = int("%s0" % mode[:3], 2)
            self.mode_permissions = int(mode[3:], 8)

            self.uid = stat.st_uid
            self.gid = stat.st_gid
            self.file_size = stat.st_size
            self.sha = sha

            # We are a bit lazy and cheat with these flags by assuming they are all 0
            self.assume_valid = 0
            self.extended_flag = 0
            self.stage_flag = 0
            self.length = len(filename)

            self.name = filename

        def pack(self) -> bytes:
            mode_b = BitArray("")
            mode_b.append(Bits(uint=self.mode_type, length=4))
            mode_b.append(Bits(uint=0, length=3))
            mode_b.append(Bits(uint=self.mode_permissions, length=9))

            sha = bytearray.fromhex(self.sha)

            flags = BitArray("")
            flags.append(Bits(uint=self.assume_valid, length=1))
            flags.append(Bits(uint=self.extended_flag, length=1))
            flags.append(Bits(uint=self.stage_flag, length=2))
            flags.append(Bits(uint=len(self.name), length=12))

            fmt = "%s%ds" % (self.ENTRY_FMT, len(self.name))
            padding = (8 - (struct.calcsize(fmt) % 8)) % 8
            fmt = "%s%dx" % (fmt, padding)
            packed = struct.pack(
                fmt,
                self.ctime,
                self.ctime_ns,
                self.mtime,
                self.mtime_ns,
                self.device,
                self.inode,
                mode_b.bytes,
                self.uid,
                self.gid,
                self.file_size,
                sha,
                flags.bytes,
                self.name.encode(),
            )

            log.debug(packed)
            return packed


def _unpack_slice(fmt: str, content: bytes, offset: int = 0):
    size = struct.calcsize(fmt)
    return struct.unpack(fmt, content[offset : offset + size])
