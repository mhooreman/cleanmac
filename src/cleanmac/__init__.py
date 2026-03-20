"""Provide the cleanmac package."""

import importlib.metadata
import pathlib

_meta = importlib.metadata.metadata("cleanmac")

__name__ = _meta.get('name')
__version__ = _meta.get('version')
__author__ = _meta.get('author')
__author_email__ = _meta.json['author_email'].split('<')[1].rsplit('>')[0]
__location__ = pathlib.Path(__file__).parent

__all__ = [
    "__name__",
    "__version__",
    "__author__",
    "__author_email__",
    "__location__",
]
