# Presentation

## Introduction: inspecting git
- git init
  - ll --tree .git
    - objects
    - refs
- echo 'content' > file && git add file
  - ll --tree .git
    - objects/d9/5f3a
    - index
- git commit -m "foo"
  - ll --tree .git
    - refs/heads/master
    - objects/07/753f
    - objects/dc/aa52
- cat-file -p

## Background: what is git
- objects
  - commit: git cat-file -p 660be1
  - tree:   git cat-file -p 5bc5be
  - blob:   git cat-file -p 3ae13c
