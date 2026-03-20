"""Test import of all the modules."""

import importlib
import pathlib
import typing

import pytest

import cleanmac


def _gen_modules_names() -> typing.Iterator[str]:
    base_path = pathlib.Path(cleanmac.__file__).parent
    for f in base_path.glob("**/*.py"):
        m = f.relative_to(base_path.parent).with_suffix("").parts
        if m[-1] == "__init__":
            m = m[:-1]
        m = ".".join(m)
        yield m


@pytest.mark.parametrize("module", list(_gen_modules_names()))
def test_module(module: str) -> None:
    """Test import of a module.

    The module is described by his classpath (a.b.c....)
    """
    importlib.import_module(module)
    assert True
