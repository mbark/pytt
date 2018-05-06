#!/usr/bin/env python
import zlib
import codecs
import hashlib
import logging
import pathlib
import bitstring

from index import Index

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
        print('%s%s %s %s\t%s' % (entry.mode_type, entry.mode_permissions, entry.sha1, entry.stage_flag, entry.name))
