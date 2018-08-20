#!/usr/bin/env bash
set -e
FILE="test.txt"

cd "$HOME/tmp"
rm -rf pytt-test
mkdir pytt-test
cd pytt-test

# create an initial repository with a first commit
git init
FILE_V0=$(echo -n 'version 0' | git hash-object -w --stdin)
git update-index 100644 "$FILE_V0" "$FILE"
TREE0=$(git write-tree)
COMMIT0=$(git commit-tree "$TREE0" -m 'initial commit')

# Create two git objects containing versions of a file
FILE_V1=$(pytt hash-object -w 'version 1')
FILE_V2=$(pytt hash-object -w 'version 2')

echo "v1: $FILE_V1"
echo "v2: $FILE_V2"

# save the version 1 file as test.txt in the current index
pytt update-index 100644 "$FILE_V1" "$FILE"

# create a tree object from the staging area (index)
TREE1=$($CMD write-tree) 

echo "tree1: $TREE"

# save the version 2 file as test.txt in the current index
pytt update-index 100644 "$FILE_V2" "$FILE"

# create a tree object from the staging area (index)
TREE2=$(pytt write-tree)

COMMIT1=$(pytt commit-tree "$TREE1" -m 'first commit' -p "$COMMIT0")
COMMIT2=$(pytt commit-tree "$TREE2" -m 'second commit' -p "$COMMIT1")

pytt update-ref refs/heads/master "$COMMIT2" 
