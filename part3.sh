#!/usr/bin/env bash

# blob
pytt hash-object -w 'updated content'
exa --tree .git

pytt cat-file dd118c

pytt update-index 100644 file dd118c
pytt write-tree

exa --tree .git

# TODO: pytt cat-file 
# TODO: add another file and create a tree with it
# TODO: commit-tree 1 and 2, 