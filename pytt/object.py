#!/usr/bin/env python
from __future__ import annotations

import logging
import textwrap
from functools import reduce
from typing import List

from bitstring import BitArray, Bits, ConstBitStream

log = logging.getLogger("pytt")


class Tree:
    """A tree roughly corresponds to a directory containing entries which can be
    either a blob or a tree.

    The object-structure looks like:
    [Tree.Entry]
    """

    def __init__(self, entries: List[Tree.Entry] = []):
        self.entries = entries

    @classmethod
    def unpack(cls, content: bytes) -> Tree:
        bits = ConstBitStream(content)
        entries = []
        while bits.pos < bits.length:
            entries.append(Tree.Entry._unpack(bits))

        return Tree(entries)

    def pack(self) -> bytes:
        bits = BitArray(b"")
        for entry in self.entries:
            bits.append(Bits(entry.pack()))

        return bits.bytes

    def __str__(self) -> str:
        s = ""
        for entry in self.entries:
            s += str(entry)

        return s

    class Entry:
        """A tree entry contains the mode and name of a tree or blob.

        If the entry describes another tree the mode will be 40000, if it
        describes a blob it will be one of the valid modes for a blob (but typically
        100644)

        The object structure looks like:
        {mode} {name}\\0{object_sha}
        """

        def __init__(self, name: str, sha: str, mode: str) -> None:
            """Create a new Entry with the given name, sha and mode. Mode can be given directly
            or as type and permissions separately (e.g. when converting from an Index.Tree"""
            self.mode = mode
            self.name = name
            self.sha = sha

        @classmethod
        def _unpack(cls, bits: BitArray) -> Tree.Entry:
            mode = _read_till(bits, b" ")
            name = _read_till(bits, b"\0")
            sha = bits.read("bytes:20").hex()

            return Tree.Entry(name, sha, mode=mode)

        def pack(self) -> bytes:
            bits = BitArray("")
            bits.append(Bits(self.mode.encode()))
            bits.append(Bits(b" "))
            bits.append(Bits(self.name.encode()))
            bits.append(Bits(b"\0"))
            bits.append(Bits(hex=self.sha))

            log.debug(bits)

            return bits.bytes

        def __str__(self) -> str:
            mode = self.mode.decode()
            if mode == "40000":
                mode = "0" + mode
                object_type = "tree"
            else:
                object_type = "blob"

            return "%s %s %s\t%s" % (mode, object_type, self.sha, self.name.decode())


class Commit:
    """A commit is a way of describing a tree and giving that tree a parent.

    A commit contains the sha of the tree it describes, an optional amount of
    parents (typically only one) as well as a description for the author
    and commiter. It also has a message describing it.

    The object-structure is:

    tree {tree_sha}
    [{parent}]
    author {author_name} <{author_email}> {author_date_seconds} {author_date_timezone}
    committer {committer_name} <{committer_email}> {committer_date_seconds} {committer_date_timezone}

    {commit message}
    """

    def __init__(
        self,
        tree: str,
        parents: List[str],
        message: str,
        author: Commit.Author = None,
        committer: Commit.Author = None,
    ):
        log.debug("tree: %s, parents: %s, message: %s" % (tree, parents, message))
        self.tree = tree
        self.message = message
        self.parents = parents

        self.author = author if author else Commit.Author()
        self.committer = committer if committer else Commit.Author()

    @classmethod
    def unpack(cls, content: bytes) -> Commit:
        bits = ConstBitStream(content)
        lines = list(bits.split(b"\n", bytealigned=True))

        lines[0].bytepos += len("tree ")
        tree = lines[0].read("bytes:40")

        index = 1
        parents = []
        while lines[index].startswith(b"\nparent"):
            lines[index].bytepos += len("\nparent ")
            parents.append(lines[index].read("bytes:40"))
            index += 1

        author = Commit.Author.unpack(lines[index], "author")
        committer = Commit.Author.unpack(lines[index + 1], "committer")

        # ignore prefix \n
        message = lines[index + 3][8:].bytes

        return Commit(tree, parents, message, author=author, committer=committer)

    def pack(self) -> bytes:
        bits = BitArray("")
        bits.append(Bits(bytes=b"tree %s\n" % self.tree.encode()))

        for parent in self.parents:
            bits.append(Bits(bytes=b"parent %s\n" % parent.encode()))

        bits.append(Bits(bytes=b"author %s\n" % self.author.pack()))
        bits.append(Bits(bytes=b"committer %s\n" % self.committer.pack()))
        bits.append(Bits(bytes=b"\n%s" % self.message.encode()))

        return bits.bytes

    def __str__(self) -> str:
        s = "tree %s\n" % self.tree.decode()
        for parent in self.parents:
            s += "parent %s\n" % parent.decode()

        s += "author %s\n" % self.author
        s += "committer %s\n" % self.committer
        s += "\n%s" % self.message.decode()

        return s

    class Author:
        """An author describes the author or committer field in a git commit.
        This is a convenience class and doesn't describe a git object.
        """

        def __init__(
            self,
            name: bytes = b"Foo Bar",
            email: bytes = b"foo.bar@email.com",
            date_s: bytes = b"1531840055",
            date_timezone: bytes = b"+0200",
        ):
            self.name = name
            self.email = email
            self.date_s = date_s
            self.date_timezone = date_timezone

        @classmethod
        def unpack(cls, line: int, prefix: str) -> Commit.Author:
            line.bytepos += len("\n%s " % prefix)
            splits = list(line.split(b" ", start=line.pos, bytealigned=True))
            date_timezone = splits[-1][8:].bytes
            date_s = splits[-2][8:].bytes
            email = splits[-3][16:-8].bytes  # strip the < when parsing
            name = reduce((lambda sum, next: sum + next.bytes), splits[:-3], b"")

            return Commit.Author(name, email, date_s, date_timezone)

        def pack(self) -> bytes:
            return str(self).encode()

        def __str__(self) -> str:
            return b" ".join(
                [self.name, b"<%s>" % self.email, self.date_s, self.date_timezone]
            ).decode()


def _read_till(bits: BitArray, delim: bytes) -> BitArray:
    start_pos = bits.pos

    found_pos = bits.findall(delim, start=bits.pos, bytealigned=True)
    next_pos = int(list(found_pos)[0] / 8)

    bits.pos = start_pos
    value = bits.read("bytes:%d" % (next_pos - bits.bytepos))

    # move past the found delimiter
    bits.bytepos += 1

    return value
