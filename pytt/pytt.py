#!/usr/bin/env python
import zlib
import codecs
import hashlib
import logging
import pathlib

import index
import tree
import commit

log = logging.getLogger('pytt')


def _git_path(path):
    return '.git/%s' % path


def _object_path(sha):
    return _git_path('objects/%s/%s' % (sha[:2], sha[2:]))


def cat_file(obj):
    with open(_object_path(obj), 'rb') as f:
        content = f.read()

    log.debug(content)

    decompressed = zlib.decompress(content)
    log.debug(decompressed)

    obj = decompressed.split(b'\0', 1)[-1]

    if decompressed.startswith(b'blob'):
        try:
            print(obj.decode())
        except UnicodeDecodeError:
            print(obj)
    elif decompressed.startswith(b'tree'):
        tree_object = tree.Tree(new=False, content=obj)
        for entry in tree_object.entries:
            print('%s %s %s\t%s' % (
                entry.mode.decode(), entry.object_type, entry.sha1, entry.name))
    elif decompressed.startswith(b'commit'):
        commit_object = commit.Commit(new=False, content=obj)
        print('tree %s' % commit_object.tree.decode())
        for parent in commit_object.parents:
            print('parent %s' % parent.decode())
        print('author %s' % commit_object.author)
        print('committer %s' % commit_object.committer)
        print('\n%s' % commit_object.message.decode())



def hash_object(content, write=False, object_type='blob'):
    header = '%s %d\0' % (object_type, len(content))
    header = header.encode()
    obj_content = header + content
    log.debug(obj_content)

    sha = hashlib.sha1(obj_content)
    print(sha.hexdigest())

    if write:
        zlib_content = zlib.compress(obj_content)
        log.debug(zlib_content)

        path = _object_path(sha.hexdigest())
        pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'wb') as f:
            f.write(zlib_content)


def ls_files():
    with open(_git_path('index'), 'rb') as f:
        content = f.read()

    idx = index.Index(content)
    for _, entry in idx.entries.items():
        # why the -1? Well the mode type is 1000, 1010 or 1100 and
        # permissions 0755 or 0644 so git decides to cut a 0 when
        # concatenating them.
        print('%s%s %s %s\t%s' % (
            bin(entry.mode_type)[2:-1], oct(entry.mode_permissions)[2:], entry.sha1, entry.stage_flag, entry.name))


def update_index(mode, sha, filename):
    entry = index.Entry(new=True, mode=mode, sha=sha, filename=filename)

    with open(_git_path('index'), 'rb') as f:
        content = f.read()
    idx = index.Index(content)
    idx.append(entry)

    packed = idx.pack()
    log.debug(content)
    log.debug(packed)

    with open(_git_path('index'), 'wb') as f:
        f.write(packed)


def write_tree():
    with open(_git_path('index'), 'rb') as f:
        content = f.read()

    idx = index.Index(content)

    tree_entries = []
    for _, entry in idx.entries.items():
        tree_entries.append(tree.Entry(new=True, mode_type=entry.mode_type, mode_permissions=entry.mode_permissions, sha=entry.sha1, name=entry.name))

    object_tree = tree.Tree(new=True, entries=tree_entries)
    content = object_tree.pack()

    log.debug(content)
    hash_object(content, write=True, object_type='tree')


def commit_tree(tree, message, parent):
    c = commit.Commit(new=True, tree=tree, message=message, parent=parent)
    content = c.pack()

    hash_object(content, write=True, object_type='commit')


def update_ref(ref, sha):
    with open(_git_path(ref), 'w') as f:
        f.write(sha)
