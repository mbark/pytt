#!/usr/bin/env bash

# Setup
pipenv shell
cd ~/tmp && rm -rf foo && mkdir foo && cd foo
export GIT_AUTHOR_DATE="Thu, 07 Apr 2005 22:13:13 +0200"
export GIT_COMMITTER_DATE="Thu, 07 Apr 2005 22:13:13 +0200"

# Part 1: What is git?

git init
exa --tree .git

# git add
echo 'constant' > file
git add file
exa --tree .git

# git commit 
git commit -m 'foo'
exa --tree .git
