#!/usr/bin/env bash

# Part 2: How does it work?

# ref: master -> commit
git rev-parse master
# commit
git cat-file -p 5b9765 
# tree
git cat-file -p 42a0df
# blob
git cat-file -p a86848