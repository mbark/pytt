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

log = logging.getLogger("pytt")


def _git_path(path: str) -> str:
    """Return the path to the file in the git-directory."""
    return ".git/%s" % path


def _ensure_directory(path: str) -> None:
    """Ensure the given path exists by creating any directories necessary."""
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)


def _resolve_object_sha(sha: str) -> str:
    """If one and only one object exists starting with the sha, return that
    objects full sha. Allows giving only the shortest sha describing an object.
    """
    directory = sha[:2]
    filename = sha[2:]

    git_dir = ".git/objects/%s" % directory
    if not os.path.isdir(git_dir):
        return sha

    matches = []
    for filepath in os.listdir(git_dir):
        if re.search("^%s.*" % filename, filepath):
            matches.append(filepath)

    if len(matches) > 1:
        log.fatal("multiple possible matches for sha %s" % sha)

    if len(matches) == 1:
        filename = matches[0]

    return "%s%s" % (directory, filename)


def _object_path(sha: str, resolve: bool = True) -> str:
    """Get the path to the object with the given sha.

    Keyword args:

    resolve -- if the sha should be resolved, set to False if you are creating
    a new object."""
    sha = _resolve_object_sha(sha) if resolve else sha
    return _git_path("objects/%s/%s" % (sha[:2], sha[2:]))


def _index() -> Index:
    """Open and parse the index."""
    with open(_git_path("index"), "rb") as f:
        return Index(f.read())


def cat_file(obj: str) -> None:
    """Print information about the given git object.

    This implementation assumes the -p flag is passed, i.e. it always pretty
    prints the object.
    """
    with open(_object_path(obj), "rb") as f:
        content = zlib.decompress(f.read())

    [header, data] = content.split(b"\0", 1)

    if header.startswith(b"blob"):
        try:
            print(data.decode())
        except UnicodeDecodeError:
            log.info("Unable to decode, printing as is")
            print(data)
    elif header.startswith(b"tree"):
        print(Tree.unpack(data))
    elif header.startswith(b"commit"):
        print(Commit.unpack(data))


def hash_object(data: bytes, write: bool = False, object_type: str = "blob") -> None:
    """Takes the given data, modifies it to git's format and prints the sha.

    {type} {length}\\0{data}

    Keyword args:
    write -- if true also saves the object to the corresponding file.
    object_type -- blob, tree or commit
    """
    header = "%s %d" % (object_type, len(data))
    content = b"%s\0%s" % (header.encode(), data)

    sha = hashlib.sha1(content)
    print(sha.hexdigest())

    if write:
        path = _object_path(sha.hexdigest(), resolve=False)
        _ensure_directory(path)

        with open(path, "wb") as f:
            f.write(zlib.compress(content))


def ls_files() -> None:
    """List all files in the index."""
    idx = _index()
    for entry in idx.get_entries():
        print(entry)


def update_index(mode: str, sha: str, filename: str) -> None:
    """Add the object (blob or tree) to the index with the mode and name."""
    idx = _index()

    idx.add_entry(Index.Entry.create(mode, _resolve_object_sha(sha), filename))

    with open(_git_path("index"), "wb") as f:
        f.write(idx.pack())


def _index_entry_mode(entry: Index.Entry) -> str:
    """Convert an index entry's mode_type and mode_permissions to a single mode string."""
    return "%s%s" % (bin(entry.mode_type)[2:-1], oct(entry.mode_permissions)[2:])


def write_tree() -> None:
    """Read the current index and create a new Tree object."""
    idx = _index()

    tree_entries = []
    for entry in idx.get_entries():
        tree_entries.append(Tree.Entry(entry.name, entry.sha, _index_entry_mode(entry)))

    tree_object = Tree(tree_entries)
    hash_object(tree_object.pack(), write=True, object_type="tree")


def commit_tree(tree: str, message: str, parent: str = None) -> None:
    """With the given tree, message and optionally parent create a new commit object and save it."""
    tree = _resolve_object_sha(tree)
    parent = _resolve_object_sha(parent)
    c = Commit(tree, [parent], message)
    hash_object(c.pack(), write=True, object_type="commit")


def update_ref(ref: str, sha: str) -> None:
    """Update the ref to the given sha."""
    sha = _resolve_object_sha(sha)
    with open(_git_path(ref), "w") as f:
        f.write(sha)
