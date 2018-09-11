#!/usr/bin/env bash

# Part 2: How does it work?

# HEAD -> ref
cat .git/HEAD

# ref: master -> commit
cat .git/refs/heads/master

# commit
git cat-file -p 5b9765 

# tree
git cat-file -p 42a0df

# blob
git cat-file -p a86848