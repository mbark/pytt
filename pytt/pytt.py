#!/usr/bin/env python
import zlib
import codecs
import hashlib
import logging
import pathlib
import bitstring

from index import Index, Entry

log = logging.getLogger('pytt')


def _path(sha):
    return '.git/objects/%s/%s' % (sha[:2], sha[2:])


def cat_file(obj):
    with open(_path(obj), 'rb') as f:
        content = f.read()

    log.debug(content)

    decompressed = zlib.decompress(content)
    log.debug(decompressed)

    if decompressed.startswith(b'commit'):
        print(decompressed.decode())
    elif decompressed.startswith(b'tree') or decompressed.startswith(b'blob'):
        object = decompressed.split(b'\0', 1)[-1]
        try:
            print(object.decode())
        except UnicodeDecodeError:
            print(object)


def hash_object(content, write):
    header = 'blob %d\0' % len(content)
    obj_content = header + content
    log.debug(obj_content)

    sha = hashlib.sha1(obj_content.encode())

    print(sha.hexdigest())

    if write:
        zlib_content = zlib.compress(obj_content.encode())
        log.debug(zlib_content)

        path = _path(sha.hexdigest())
        pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'wb') as f:
            f.write(zlib_content)


def ls_files():
    with open('.git/index', 'rb') as f:
        content = f.read()

    index = Index(content)
    for entry in index.entries:
        # why the -1? Well the mode type is 1000, 1010 or 1100 and
        # permissions 0755 or 0644 so git decides to cut a 0 when
        # concatenating them.
        print('%s%s %s %s\t%s' % (
            bin(entry.mode_type)[2:-1], oct(entry.mode_permissions)[2:], entry.sha1, entry.stage_flag, entry.name))


def update_index(mode, sha, filename):
    entry = Entry(new=True, mode=mode, sha=sha, filename=filename)
    entry.pack()
    print('TODO')
