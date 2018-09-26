#!/usr/bin/env bash
set -eo pipefail

# Setup
# pipenv shell
cd ~/tmp && rm -rf quotations && mkdir quotations && cd quotations
export GIT_AUTHOR_DATE="Thu, 07 Apr 2005 22:13:13 +0200"
export GIT_COMMITTER_DATE="Thu, 07 Apr 2005 22:13:13 +0200"

git init

# git add
echo '"The problem with quotes on the Internet is that it is hard to verify their authenticity." ~ Abraham Lincoln' >quotation.txt
git add quotation.txt

# git commit
git commit -m 'Add legit quote by e = mc2 dude'
