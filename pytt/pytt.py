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


def cat_file(obj):
    """Print information about the given git object.

    This implementation assumes the -p flag is passed, i.e. it always pretty
    prints the object.
    """
    with open(_object_path(obj), 'rb') as f:
        content = zlib.decompress(f.read())

    [metadata, obj] = content.split(b'\0', 1)

    if metadata.startswith(b'blob'):
        try:
            print(obj.decode())
        except UnicodeDecodeError:
            log.debug('Unable to decode, printing as is')
            print(obj)
        pass
    elif metadata.startswith(b'tree'):
        tree_object = Tree.from_string(obj)
        for entry in tree_object.entries:
            mode = entry.mode.decode()
            if mode == '40000':
                mode = '0' + mode
                object_type = 'tree'
            else:
                object_type = 'blob'

            print('%s %s %s\t%s' % (
                mode, object_type, entry.sha1, entry.name.decode()))
    elif metadata.startswith(b'commit'):
        commit_object = Commit.from_string(obj)
        print('tree %s' % commit_object.tree.decode())
        for parent in commit_object.parents:
            print('parent %s' % parent.decode())
        print('author %s' % commit_object.author)
        print('committer %s' % commit_object.committer)
        print('\n%s' % commit_object.message.decode())


def hash_object(data, write=False, object_type='blob'):
    """Takes the given data, modifies it to git's format and prints the sha.

    Keyword args:
    write -- if true also saves the object to the corresponding file.
    object_type -- blob, tree or commit 

    {type} {length}\\0{data}
    """
    header = '%s %d\0' % (object_type, len(data))
    header = header.encode()
    content = header + data

    sha = hashlib.sha1(content)
    print(sha.hexdigest())

    if write:
        path = _object_path(sha.hexdigest())
        pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'wb') as f:
            f.write(zlib.compress(content))


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


def update_index(mode, sha, filename):
    """Add the object (blob or tree) to the index with the mode and name."""
    idx = _index()

    idx.append(Index.Entry(new=True, mode=mode, sha=sha, filename=filename))

    packed = idx.pack()
    with open(_git_path('index'), 'wb') as f:
        f.write(packed)


def write_tree():
    """Write the index to a git tree."""
    idx = _index()

    tree_entries = []
    for _, entry in idx.entries.items():
        tree_entries.append(Tree.Entry(mode_type=entry.mode_type,
                                       mode_permissions=entry.mode_permissions, sha=entry.sha1, name=entry.name))

    tree_object = Tree(tree_entries)
    hash_object(tree_object.pack(), write=True, object_type='tree')


def commit_tree(tree, message, parent=None):
    """Create a commit for the tree."""
    tree = _resolve_object_sha(tree)
    parent = _resolve_object_sha(parent)
    c = Commit.create(tree, message, parent)
    hash_object(c.pack(), write=True, object_type='commit')


def update_ref(ref, sha):
    """Update the ref to the given sha."""
    sha = _resolve_object_sha(sha)
    with open(_git_path(ref), 'w') as f:
        log.info('writing %s to %s' % (sha, _git_path(ref)))
        f.write(sha)
