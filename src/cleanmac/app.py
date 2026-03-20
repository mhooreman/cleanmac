"""Provide the cleanmac project's application."""

import pathlib

import click

from . import commands

_DIRECTORY_ARGUMENT = click.argument(
    "directory",
    nargs=-1,
    required=True,
    type=click.Path(
        # Can be read-only as deleting can be an option
        exists=True, file_okay=False, resolve_path=True,
        path_type=pathlib.Path,
    )
)

_REMOVE_OR_KEEP_OPTION = click.option(
    "--remove/--keep",
    help="Remove or keep identified entries.",
    default=False,
    show_default=True
)

_LICENSE_MSG = """
The 3-Clause BSD License
------------------------

Copyright 2026-today Michaël Hooreman <mhooreman_AT_icloud_DOT_com>

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors
   may be used to endorse or promote products derived from this software
   without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
""".strip()


@click.group(invoke_without_command=True)
@click.version_option()
@click.option(
    "--showlicense", is_flag=True,
    help="Show copyright and license information and exit."
)
@click.pass_context
def main(ctx: click.Context, *, showlicense: bool) -> None:
    """Clean MacOS."""
    if showlicense:
        click.echo(_LICENSE_MSG)
        raise SystemExit(0)
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        ctx.exit(1)


@main.command()
@_DIRECTORY_ARGUMENT
@_REMOVE_OR_KEEP_OPTION
def symlinks(*, directory: tuple[pathlib.Path, ...], remove: bool) -> None:
    """Detect and eventually remove symbolic links in selected directories."""
    commands.Symlinks(paths=directory, remove=remove)()


@main.command()
@_DIRECTORY_ARGUMENT
@_REMOVE_OR_KEEP_OPTION
def dsstore(*, directory: tuple[pathlib.Path, ...], remove: bool) -> None:
    """Detect and eventually remove .DS_Store files in selected directories."""
    commands.Unconditional(
        paths=directory, patterns=("**/.DS_Store", ), remove=remove
    )()


@main.command()
@_DIRECTORY_ARGUMENT
@_REMOVE_OR_KEEP_OPTION
def pycache(*, directory: tuple[pathlib.Path, ...], remove: bool) -> None:
    """Detect and eventually remove python cache in selected directories."""
    commands.Unconditional(
        paths=directory, patterns=("**/__pycache__", ), remove=remove
    )()


@main.command()
@_DIRECTORY_ARGUMENT
@_REMOVE_OR_KEEP_OPTION
def venv(*, directory: tuple[pathlib.Path, ...], remove: bool) -> None:
    """Detect and eventually remove python venvs in selected directories."""
    commands.Unconditional(
        paths=directory, patterns=("**/.venv", ), remove=remove
    )()


@main.command()
@_REMOVE_OR_KEEP_OPTION
def ospackages(*, remove: bool) -> None:
    """Detect and eventually remove MacOS packages which disappeared.

    Apple packages are excluded.
    """
    commands.OSPackages(remove=remove)()
