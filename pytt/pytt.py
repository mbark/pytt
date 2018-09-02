#!/usr/bin/env python
import codecs
import hashlib
import logging
import os
import pathlib
import re
import zlib

from .index import Index
from .object import Commit, Tree

log = logging.getLogger('pytt')


def _git_path(path):
    return '.git/%s' % path


def _resolve_object_sha(sha):
    """If one and only one object exists starting with the sha, return that
    objects full sha. Allows giving only the shortest sha describing an object.
    """
    directory = sha[:2]
    filename = sha[2:]
    
    git_dir = '.git/objects/%s' % directory
    if not os.path.isdir(git_dir):
        return sha

    matches = []
    for filepath in os.listdir(git_dir):
        if re.search('^%s.*' % filename, filepath):
            matches.append(filepath)

    if len(matches) > 1:
        log.fatal('multiple possible matches for sha %s' % sha)

    if len(matches) == 1:
        filename = matches[0]

    return '%s%s' % (directory, filename)


def _object_path(sha):
    sha = _resolve_object_sha(sha)
    return _git_path('objects/%s/%s' % (sha[:2], sha[2:]))


def _index():
    """Open and parse the index."""
    with open(_git_path('index'), 'rb') as f:
        return Index(f.read())


def ls_files():
    """List all files in the index."""
    idx = _index()
    for _, entry in idx.entries.items():
        # why the -1? Well the mode type is 1000, 1010 or 1100 and
        # permissions 0755 or 0644 so git decides to cut a 0 when
        # concatenating them.
        mode = '%s%s' % (bin(entry.mode_type)[
                         2:-1], oct(entry.mode_permissions)[2:])
        print('%s %s %s\t%s' % (
            mode, entry.sha1, entry.stage_flag, entry.name))


def cat_file(obj):
    """Print information about the given git object.

    This implementation assumes the -p flag is passed, e.g. it always pretty
    prints the object.
    """
    metadata = b''

    if metadata.startswith(b'blob'):
        pass
    elif metadata.startswith(b'tree'):
        pass
    elif metadata.startswith(b'commit'):
        pass


def hash_object(obj, write=False, object_type='blob'):
    """Takes the given data, modifies it to git's format and prints the sha.

    Keyword args:
    write -- if true also saves the object to the corresponding file.
    object_type -- blob, tree or commit
    """

    if write:
        pass


def update_index(mode, sha, filename):
    """Add the object (blob or tree) to the index with the mode and name."""
    pass


def write_tree():
    """Write the index to a git tree."""
    pass


def commit_tree(tree, message, parent=None):
    """Create a commit for the tree."""
    pass


def update_ref(ref, sha):
    """Update the ref to the given sha."""
    pass
