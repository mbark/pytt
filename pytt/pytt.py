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
        
    def hexer(start):
        def hex (i,j): return codecs.encode(content[start+i:start+j], 'hex_codec')
        return hex
           
    hex = hexer(0)
    
    files = int(hex(8, 12), 10)
    
    log.debug(""" index file:
DIRC: %s
Version: %s
File count: %s
""" % (content[:4], hex(4, 8), files))
    
    position = 12
    for i in range(0, files):
        size = 62
        hex = hexer(position)

        mode = bitstring.BitArray(content[position+24:position+28])[16:]
        
        log.debug(""" index entry #%s:
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
""" % (i, hex(0, 8), hex(8, 16), hex(16, 20), hex(20, 24), mode[:4].bin, mode[7:].oct, hex(28, 32), hex(32, 36), hex(36, 40), hex(40, 60), hex(60, 62)[:1]))
        
        length = int(hex(60, 62)[1:], 16)
        padding = (8 - (size+length % 8)) % 8
        
        file = content[position+size:]

        log.debug(""" index entry (file info):
Length: %s
Name: %s
Remaining (null-terminated): %s
    """ % (length, file[:length], file[length:length+padding]))
        
        print('%s%s %s %s\t%s' % (mode[:4].bin, mode[7:].oct, hex(40, 60), hex(60, 62)[:1], file[:length]))
        position = position + size + length + padding

    log.debug('checksum: %s', bitstring.BitArray(content[-20:]).hex)
    log.debug('remaining: %s, size: %s', content[position:], len(content[position:]))
    if(len(content[position:]) > 20):
        log.debug('extensions (ignoring parsing these): %s', content[position:-20])
        return
