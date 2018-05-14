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


## TODO
- [x] `cat-file`
- [x] `hash-object`
- [x] `ls-files`
- [ ] `update-index`
- [ ] `write-tree`
- [ ] `commit-tree`
- [ ] `update-ref`
