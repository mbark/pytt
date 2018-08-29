#!/usr/bin/env bash

# Setup
cd ~/tmp
rm -rf foo

mkdir foo
cd foo

git init
exa --tree .git

# git add
echo 'constant' > file
git add file
exa --tree .git

# git commit 
export GIT_AUTHOR_DATE="Thu, 07 Apr 2005 22:13:13 +0200"
export GIT_COMMITTER_DATE="Thu, 07 Apr 2005 22:13:13 +0200"
git commit -m 'foo'
exa --tree .git
