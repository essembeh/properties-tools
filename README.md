![Github](https://img.shields.io/github/tag/essembeh/properties-diff.svg)
![PyPi](https://img.shields.io/pypi/v/properties-diff.svg)
![Python](https://img.shields.io/pypi/pyversions/properties-diff.svg)


# properties-diff

Command line tool to compare *properties* files and print differences with colors as if you were using `diff` or `colordiff` tools.

Even if *properties* files are text files, using directly `diff` is not that efficient because of key/value pairs order or format (for example using `=` or `[space]=[space]` as separator, double quoting values...). `properties-diff` compare key/value pairs but not the order nor the format.

# Usage

```sh
$ properties-diff --help
usage: properties-diff [-h] [-q] [--quote] [--sep SEP] [-m {simple,diff,wdiff}] left.properties right.properties

positional arguments:
  left.properties       left file to compare
  right.properties      right file to compare

optional arguments:
  -h, --help            show this help message and exit
  -q, --quiet           print less information
  --quote               use double quotes for values, example: foo="bar"
  --sep SEP             key/value separator, default is '='
  -m {simple,diff,wdiff}, --mode {simple,diff,wdiff}
                        select a format to show differences: using colors only (simple), using diff-like format (diff) or wdiff-like
                        (wdiff) format. Default is 'diff'
```

## Modes


You can see differences between the properties files using 3 modes using `--mode <MODE>`
* `simple`, based on colors, *red* for removed lines, *green* for added lines
* `diff`, prints the changes like `diff` tool would do (this is the default mode)
* `wdiff`, prints the changes like `wdiff` tool would do

![simple](images/simple.png)
![diff](images/diff.png)
![wdiff](images/wdiff.png)


# Install

Install from the sources
```sh
$ pip3 install --user --upgrade git+https://github.com/essembeh/properties-diff
$ properties-diff path/to/file.properties path/to/another/file.properties
```

Install the latest release from [PyPI](https://pypi.org/project/properties-diff/)
```sh
$ pip3 install --user --upgrade properties-diff
$ properties-diff path/to/file.properties path/to/another/file.properties
```
