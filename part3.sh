#!/usr/bin/env bash

# blob
pytt hash-object -w 'updated content'
exa --tree .git

pytt cat-file dd118c

# index + tree
pytt update-index 100644 dd118c file
pytt write-tree

exa --tree .git

pytt cat-file 3ae13c