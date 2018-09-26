#!/usr/bin/env python
from __future__ import annotations


def test_write_read_file(tmpdir):
    """Write to a file, read from it and verify the output is the same.

    with open(filename, {flags}) as f:
        f.{operation}(content)

    where:
    -- flags is 'r' to read, 'w' to write and 'b' if it is a binary string
    -- operation is either read or write;
    """
    output = 'output'
    read = ''

    some_file = tmpdir.join('file')
    assert read == output


def test_from_string_to_bytes():
    """Convert from a string to a bytes string."""
    assert "a string" == b"a string"


def test_from_bytes_to_string():
    """Convert from a bytes string to an encoded string."""
    assert b"a string" == "a string"


def test_add_to_list():
    """Use append to add any element to the list."""
    l = []

    assert len(l) == 1


def test_iterate_over_list():
    """Iterate over the list and sum the values.

    for val in list:
        # do something with value"""
    l = [1, 2, 3, 4, 5]

    sum = 0

    assert sum == 15


def test_string_concatenation():
    """Use pythonic string formatting, i.e.: '%s %s' % (str1, str2)"""
    s = '' % (22, 'bar')

    assert s == '22 bar'


def test_string_concatenation_with_bytes():
    """Use pythonc string formatting with byte strings"""
    s = b'' % (b'foo', '123')

    assert s == b'foo 123'


def test_create_class_instance():
    """Create a new instance of the class TestClass."""
    instance = None
    param = 'foo'

    assert instance.param == param


def test_use_class_method():
    """Create an instance of ClassMethod and call do_stuff on it."""
    instance = None
    arg = 'bar'

    assert instance.arg == arg


def test_use_classmethod():
    """Create an instance of ClassMethod using the static method a_static_doer."""
    instance = None
    param = 'param'

    assert instance is not None
    assert instance.param == param


class SomeClass:
    def __init__(self, param: str, arg = None) -> None:
        self.param = param

    def do_stuff(self, arg: str) -> str:
        self.arg = arg

    @classmethod
    def a_static_doer(cls, param) -> TestClass:
        return TestClass(param)
