#!/usr/bin/env python
import zlib
import codecs
import hashlib
import logging
import pathlib
import bitstring


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
        
    def hex (i, j): return codecs.encode(content[i:j], 'hex_codec')
    
    index = bitstring.BitArray(content)
    
    log.debug(""" index file:
DIRC: %s
Version: %s
File count: %s
""" % (content[:4], hex(4, 8), hex(8, 12)))
    
    mode = bitstring.BitArray(content[36:40])[16:]
    length = int(hex(72, 74)[1:], 10)
    padding = (8 - (7 % 8)) % 8
    
    log.debug(""" index entry #0:
ctime: %s
mtime: %s
device: %s
inode: %s
mode:
    type %s
    unix permission: %s
UID: %s
GID: %s
File size: %s
Entry SHA-1: %s
Flags: %s
Length: %s
Index SHA-1: %s
Remaining (null-terminated): %s
""" % (hex(12, 20), hex(20, 28), hex(28, 32), hex(32, 36), mode[:4].bin, mode[7:].oct, hex(40, 44), hex(44, 48), hex(48, 52), hex(52, 72), hex(72, 74)[:1], length, content[74:74+length], content[74+length:74+length+padding]))
