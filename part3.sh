#!/usr/bin/env bash

# Part 3: How does it all tie together?

# blob
pytt hash-object -w 'updated content'
exa --tree .git

pytt cat-file dd118c

# index + tree
pytt update-index 100644 dd118c file
pytt ls-files
pytt write-tree

exa --tree .git

pytt cat-file 3ae13c

# commit
pytt commit-tree -p 660be1 -m 'our first commit' 3ae13c
exa --tree .git 

# ref 
pytt update-ref refs/heads/master 510a08

# it all ties together :tada:
git log