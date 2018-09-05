#!/usr/bin/env bash

# Setup
pipenv shell
cd ~/tmp && rm -rf quotations && mkdir quotations && cd quotations
export GIT_AUTHOR_DATE="Thu, 07 Apr 2005 22:13:13 +0200"
export GIT_COMMITTER_DATE="Thu, 07 Apr 2005 22:13:13 +0200"

# Part 1: What is git?

git init
exa --tree .git

# git add
echo '"The problem with quotes on the Internet is that it is hard to verify their authenticity." ~ Abraham Lincoln' > quotation.txt
git add quotation.txt
exa --tree .git

# git commit 
git commit -m 'Add legit quote by e = mc2 dude'
exa --tree .git
