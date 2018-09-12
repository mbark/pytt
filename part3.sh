#!/usr/bin/env bash

# Part 3: How does it all tie together?

# blob
pytt hash-object -w '"The greatest thing about Facebook is that you can quote something and totally make up the source." ~ George Washington'
exa --tree .git

pytt cat-file 291d4c

# index + tree
pytt update-index 100644 291d4c quotation.txt
pytt ls-files
pytt write-tree

# commit
# bug!
pytt commit-tree -p 5b9765 -m 'Oops! Wrong dude, this is the real one!' e04427

# ref 
pytt update-ref refs/heads/master e6a5d5

# it all ties together :tada:
git log