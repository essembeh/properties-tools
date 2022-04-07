![Github](https://img.shields.io/github/tag/essembeh/properties-diff.svg)
![PyPi](https://img.shields.io/pypi/v/properties-diff.svg)
![Python](https://img.shields.io/pypi/pyversions/properties-diff.svg)
![](https://github.com/essembeh/properties-diff/actions/workflows/poetry.yml/badge.svg)


# properties-diff

`properties-diff` is a command line tools to compare *properties* files and print differences with colors as if you were using `wdiff` or `diff` tools.

Even if *properties* files are text files, using directly `diff` is not that efficient because of key/value pairs order or format (for example using `=` or `[space]=[space]` as separator, double quoting values...). `properties-diff` compare key/value pairs but not the order nor the format.

`properties-patch` is a command line tools to patch a *properties* files with one or more *properties* files to add, update or delete some properties.



# Install

Install the latest release from [PyPI](https://pypi.org/project/properties-diff/)
```sh
$ pip3 install properties-diff
$ properties-diff path/to/file.properties path/to/another/file.properties
```

Install from the sources
```sh
$ pip3 install --user --upgrade git+https://github.com/essembeh/properties-diff
$ properties-diff path/to/file.properties path/to/another/file.properties
```


# Usage

```sh
$ properties-diff --help                                                                                                                               130
usage: properties-diff [-h] [-q] [--quote] [--sep SEP] [-m {simple,diff,wdiff}] [-A] [-D] [-U] left.properties right.properties

positional arguments:
  left.properties       left file to compare
  right.properties      right file to compare

optional arguments:
  -h, --help            show this help message and exit
  -q, --quiet           print less information
  --quote               use double quotes for values, example: foo="bar"
  --sep SEP             key/value separator, default is '='
  -m {simple,diff,wdiff}, --mode {simple,diff,wdiff}
                        select a format to show differences: using colors only (simple), using diff-like format (diff) or wdiff-like (wdiff) format. Default is 'wdiff'
  -A, --added           print added properties
  -D, --deleted         print deleted properties
  -U, --updated         print updated properties

```


```sh
$ properties-patch --help
usage: properties-patch [-h] [-c] [--comments] [-f] [-i] [--quote] [--sep SEP] [-A] [-D] [-U] -p patch.properties [-o output.properties] source.properties

positional arguments:
  source.properties     file to modify

optional arguments:
  -h, --help            show this help message and exit
  -c, --color           print colors
  --comments            insert comment when property is added, updated or deleted
  -f, --force           force output file (--output) overwrite if it already exists
  -i, --interactive     ask for confirmation to add, update or delete a property
  --quote               use double quotes for values, example: foo="bar"
  --sep SEP             key/value separator, default is '='
  -p patch.properties, --patch patch.properties
                        patch file
  -o output.properties, --output output.properties
                        modified file

  -A, --add             add new properties from patches
  -D, --delete          delete properties not in patches
  -U, --update          update properties from patches

```


## properties-diff modes

You can see differences between the properties files using 3 modes using `--mode <MODE>` or `-m <MODE>`
* `wdiff`, prints the changes like `wdiff` tool would do (this is the default mode)
* `diff`, prints the changes like `diff` tool would do
* `simple`, based on colors, *red* for removed lines, *green* for added lines

![wdiff](images/wdiff.png)
![diff](images/diff.png)
![simple](images/simple.png)
