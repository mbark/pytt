#!/usr/bin/env bash

cd ~/tmp/quotations

# HEAD -> ref
cat .git/HEAD

# ref: master -> commit
cat .git/refs/heads/master

# commit
git cat-file -p b60cec

# tree
git cat-file -p 42a0df

# blob
git cat-file -p a86848
