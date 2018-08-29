#!/usr/bin/env bash

cd ~/tmp/foo

# commit
pytt commit-tree -p 660be1 -m 'our first commit' 3ae13c
exa --tree .git 

# ref

pytt update-ref refs/heads/master 510a08