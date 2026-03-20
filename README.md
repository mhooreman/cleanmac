# cleanmac

## Introduction

This package provides a command line tool to perform various cleaning
operations on Mac OS which are not handled by common cleaning tools like
CCleaner.

## Installation

This tool needs python >= 3.12 on any version of MacOS.

### Using `uv`

This is the recommanded way. Please see the
[UV documentation](https://docs.astral.sh/uv/)
.

Simply replace the url of the chosen version in the command below.

``uv tool install https://github.com/mhooreman/cleanmac/releases/download/0.1.0/cleanmac-0.1.0-py3-none-any.whl``

It will install the tool in a dedicated environment and will provide the
`cleanmac` command line without any additional complexity.

### Using `pip`

While not recommended, if is available if you are not able to or don't wan't to
use uv.

Since this is the standard python package management process, this is out of
scope of the current document.

## Usage

## Development

Develoment shall be done using uv. Please refer to the
[official documentation](https://docs.astral.sh/uv/)
of that tool.

Quality control rules are fixed in the pyproject.toml file. The following shall
be applied:

- `uv run ruff check`
- `uv run mypy`
- `uv run pytest`

Those three quality control tools shall be executed with the supported python
versions. That can be achieved using `uv --python 3.xx command arguments`.

## Changelog

# 0.1.1

- #2: Justfile removed

- #3: Completed README.md

- #4: unit test don't rely on `__location__` anymore

- #5: checking if running on MacOS at startup

- #6: Now python >= 3.12 is supported (was only 3.14 before)

- #7: A `toolbox` package is provided for commonalities. Async external command
  run with easier processing now part of that package.

# 0.1.0

- Initial release

## About

Copyright (C) 2026-Today Michael Hooreman

Released under the 3 clauses MIT license, see LICENSE.md
