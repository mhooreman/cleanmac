"""Provide the cleanmac project's application."""

import click


class _App:
    """The main application class.

    It provides a runnable instance.
    """

    def __call__(self) -> None:
        """Run the instance."""
        click.echo("Hello, World")


@click.command()
@click.version_option(package_name="cleanmac")
def main() -> None:
    """Start the cleanmac main application."""
    _App()()
