#!/usr/bin/env python
import argparse
import json
import logging
import sys

import colorlog

from . import pytt

log = logging.getLogger('pytt')
log_levels = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'fatal': logging.FATAL
}
log_names = list(log_levels)


def run():
    args = _parse_args()
    _set_up_logging(args)

    if args.command == 'cat-file':
        pytt.cat_file(args.object)
    elif args.command == 'hash-object':
        pytt.hash_object(args.content.encode(), args.write)
    elif args.command == 'ls-files':
        pytt.ls_files()
    elif args.command == 'update-index':
        pytt.update_index(args.mode, args.sha, args.filename)
    elif args.command == 'write-tree':
        pytt.write_tree()
    elif args.command == 'commit-tree':
        pytt.commit_tree(args.tree, args.message, args.parent)
    elif args.command == 'update-ref':
        pytt.update_ref(args.ref, args.sha)
    else:
        print('unknown command %s' % args.command)


def _parse_args():
    parser = argparse.ArgumentParser(
        description="pytt",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    subparsers = parser.add_subparsers(dest='command')

    hash_obj = subparsers.add_parser('hash-object')
    hash_obj.add_argument('content')
    hash_obj.add_argument('-w', '--write',
                          action='store_true',
                          help='save the object as well')

    cat_file = subparsers.add_parser('cat-file')
    cat_file.add_argument('object')

    subparsers.add_parser('ls-files')

    update_index = subparsers.add_parser('update-index')
    update_index.add_argument('mode')
    update_index.add_argument('sha')
    update_index.add_argument('filename')

    subparsers.add_parser('write-tree')

    commit_tree = subparsers.add_parser('commit-tree')
    commit_tree.add_argument('tree', help='tree to commit')
    commit_tree.add_argument('-p', '--parent', help='commit parent')
    commit_tree.add_argument('-m', '--message', help='commit message')

    update_ref = subparsers.add_parser('update-ref')
    update_ref.add_argument('ref', help='the ref to update')
    update_ref.add_argument('sha', help='the sha to set the ref to')

    parser.add_argument(
        '-l',
        '--log-level',
        default=log_names[1],
        choices=log_names,
        help='The log level for the client')

    return parser.parse_args()


def _set_up_logging(args):
    handler = colorlog.StreamHandler()
    formatter = colorlog.ColoredFormatter(
        fmt=('%(log_color)s[%(asctime)s %(levelname)8s] --'
             ' %(message)s (%(filename)s:%(lineno)s)'),
        datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)

    log.addHandler(handler)
    log.setLevel(log_levels[args.log_level])
