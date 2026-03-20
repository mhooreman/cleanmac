"""Provide logging features."""

import logging
import os
import pathlib
import sys
import typing

_STRIP_PATH_CHARS: typing.Final[int] = len(
    str(pathlib.Path(__file__).parent.parent)
) + 1


def _add_qualmod(record: logging.LogRecord) -> logging.LogRecord:
    record.qualmod = record.pathname[
        _STRIP_PATH_CHARS:
    ].rsplit(".", 1)[0].replace(os.path.sep, ".")
    return record


def _get_logger() -> logging.Logger:
    lg = logging.getLogger(__name__.split(".", 1)[0])
    lg.setLevel(logging.DEBUG)
    ha = logging.StreamHandler(
        # to stdout as it is the only output, and might be piped
        stream=sys.stdout
    )
    ha.setLevel(logging.DEBUG)
    fo = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(qualmod)s@%(lineno)d:%(funcName)s "
        "- %(message)s"
    )
    ha.addFilter(_add_qualmod)
    ha.setFormatter(fo)
    lg.addHandler(ha)
    return lg


logger: typing.Final[logging.Logger] = _get_logger()
