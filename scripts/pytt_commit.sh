#!/usr/bin/env bash
set -eo pipefail

cd ~/tmp/quotations
command -v pytt >/dev/null 2>&1 || {
	echo >&2 "pytt not found, are you running this inside a pipenv shell"
	exit 1
}

# blob
pytt hash-object -w '"The greatest thing about Facebook is that you can quote something and totally make up the source." ~ George Washington'

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
