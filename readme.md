# WIP 🚧

```shell
$ ./pytt/cli.py cat-file 3c7b109738e60831c50f5680dfe664120367ddba
```

```shell
$ ./pytt/cli.py hash-object 'what is up, doc?' -w
bd9dbf5aae1a3862dd1526723246b20206e5fc37
$ git cat-file -p bd9dbf5aae1a3862dd1526723246b20206e5fc37
what is up, doc?
```

```shell
$ ./pytt/cli.py -l info ls-files
1000644 7a591e1b3cb7bb048e0662b5079f0fd7ad3e971d 0      LICENSE
1000644 18f591b550cd7b80ffac7e9e1d1aa08eec87bb42 0      Pipfile
1000644 af13cf905a6d8996c99091a5649c88b4e2e84f96 0      Pipfile.lock
1000755 e4a3cc7e36f440925101fb67765a8a2d0418c821 0      pytt/__init__.py
1000755 ecb315b707299085b83e81ceca78304628cdf711 0      pytt/cli.py
1000755 79c9d63bcf59c4f257f3f29e2f749450dd49ac28 0      pytt/index.py
1000755 fb0508fcfa972c6202a7f23700cbbd348706f165 0      pytt/pytt.py
1000644 e99000226891fa0e7965a5a45d94154568575235 0      readme.md

$ git ls-files -s # literally the same
```

``` shell
$ ./pytt/cli.py hash-object 'what is up, doc?' -w
$ ./pytt/cli.py update-index 100644 bd9dbf5aae1a3862dd1526723246b20206e5fc37 afile
$ git status
# Changes to be committed:
#   (use "git rm --cached <file>..." to unstage)
#
#        new file:   afile
#
```

``` shell
$ ./pytt/cli.py hash-object 'what is up, doc?' -w
$ ./pytt/cli.py update-index 100644 bd9dbf5aae1a3862dd1526723246b20206e5fc37 afile
$ ./pytt/cli.py write-tree
23a890411c06cd26c7e9e86d13d23197b9b06967 # will vary depending on index
$ git cat-file -p 23a890411c06cd26c7e9e86d13d23197b9b06967
# ...
```

``` shell
$ ./pytt/cli.py cat-file $(git rev-parse HEAD)
# tree e227e810aa558bae7324940e521d031ed35b6cdc
# author Martin Barksten <martin.barksten@gmail.com> 1531833735 +0200
# committer Martin Barksten <martin.barksten@gmail.com> 1531833735 +0200

# foo
```

``` shell
$ ./pytt/cli.py write-tree
# 4b825dc642cb6eb9a060e54bf8d69288fbee4904
$ ./pytt/cli.py commit-tree 4b825dc642cb6eb9a060e54bf8d69288fbee4904 -m 'foo: message' -p $(git rev-parse HEAD)
# 6f0607cd1706763df9f2200607124386cd89efb9
$ ./pytt/cli.py cat-file 6f0607cd1706763df9f2200607124386cd89efb9
# ...
```

``` shell
$ ./pytt/cli.py write-tree
$ ./pytt/cli.py commit-tree 4b825dc642cb6eb9a060e54bf8d69288fbee4904 -m 'foo: message' -p $(git rev-parse HEAD)
# 6f0607cd1706763df9f2200607124386cd89efb9
$ ./pytt/cli.py update-ref refs/heads/another 6f0607cd1706763df9f2200607124386cd89efb9
# Switched to branch 'another'
```
