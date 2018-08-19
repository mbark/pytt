#!/usr/bin/env python
import codecs
import hashlib
import logging
import pathlib
import zlib

from .index import Index
from .object import Commit, Tree

log = logging.getLogger('pytt')


def _git_path(path):
    return '.git/%s' % path


def _object_path(sha):
    return _git_path('objects/%s/%s' % (sha[:2], sha[2:]))


def _index():
    with open(_git_path('index'), 'rb') as f:
        return Index(f.read())


def cat_file(obj):
    with open(_object_path(obj), 'rb') as f:
        content = zlib.decompress(f.read())

    [metadata, obj] = content.split(b'\0', 1)

    if metadata.startswith(b'blob'):
        try:
            print(obj.decode())
        except UnicodeDecodeError:
            log.debug('Unable to decode, printing as is')
            print(obj)
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


def hash_object(obj, write=False, object_type='blob'):
    header = '%s %d\0' % (object_type, len(obj))
    header = header.encode()
    content = header + obj

    sha = hashlib.sha1(content)
    print(sha.hexdigest())

    if write:
        path = _object_path(sha.hexdigest())
        pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'wb') as f:
            f.write(zlib.compress(content))


def ls_files():
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
    idx = _index()

    idx.append(Index.Entry(new=True, mode=mode, sha=sha, filename=filename))

    packed = idx.pack()
    with open(_git_path('index'), 'wb') as f:
        f.write(packed)


def write_tree():
    idx = _index()

    tree_entries = []
    for _, entry in idx.entries.items():
        tree_entries.append(Tree.Entry(mode_type=entry.mode_type,
                                       mode_permissions=entry.mode_permissions, sha=entry.sha1, name=entry.name))

    tree_object = Tree(tree_entries) 
    hash_object(tree_object.pack(), write=True, object_type='tree')


def commit_tree(tree, message, parent):
    c = Commit.create(tree, message, parent) 
    hash_object(c.pack(), write=True, object_type='commit')


def update_ref(ref, sha):
    with open(_git_path(ref), 'w') as f:
        f.write(sha)
