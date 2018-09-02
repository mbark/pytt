#!/usr/bin/env bash

# Part 2: How does it work?

# ref: master -> commit
git rev-parse master
# commit
git cat-file -p 660be1 
# tree
git cat-file -p 3ae13c
# blob
git cat-file -p 5bc5be