# WIP 🚧

```shell
$ ./pytt/cli.py cat-file 3c7b109738e60831c50f5680dfe664120367ddba
```

```shell
$ ./pytt/cli.py hash-object 'what is up, doc?' -w
# ...
$ git cat-file -p bd9dbf5aae1a3862dd1526723246b20206e5fc37
what is up, doc?
```

```shell
$ ./pytt/cli.py -l info ls-files
1000644 b'7a591e1b3cb7bb048e0662b5079f0fd7ad3e971d' b'0'        b'LICENSE'
1000644 b'18f591b550cd7b80ffac7e9e1d1aa08eec87bb42' b'0'        b'Pipfile'
1000644 b'af13cf905a6d8996c99091a5649c88b4e2e84f96' b'0'        b'Pipfile.lock'
1000755 b'e4a3cc7e36f440925101fb67765a8a2d0418c821' b'0'        b'pytt/__init__.py'
1000755 b'2b2df8ff73e2fe91e6c6091b99b435bf7d7c17ac' b'0'        b'pytt/cli.py'
1000755 b'2d077129d72414b2761ca0874c929416606bdccb' b'0'        b'pytt/pytt.py'
1000644 b'966c4f7af8cb61660e062c41769e55f93e2dd105' b'0'        b'readme.md'
$ git ls-files -s # compare output
```


## TODO
- [x] `cat-file`
- [x] `hash-object`
- [x] `ls-files`
- [ ] `update-index`
- [ ] `write-tree`
- [ ] `commit-tree`
- [ ] `update-ref`
