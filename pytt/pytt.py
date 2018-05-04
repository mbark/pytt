#!/usr/bin/env python
import zlib
import logging


log = logging.getLogger('pytt')

def cat_file(obj):
    with open('.git/objects/%s/%s' % (obj[:2], obj[2:]), 'rb') as f:
        content = f.read()

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
