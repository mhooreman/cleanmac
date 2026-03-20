"""Various tools."""

import asyncio
import asyncio.subprocess
import subprocess  # noqa: S404
import sys
import typing

_EXPECTED_PLATFORM: typing.Final[str] = "darwin"


class UnsupportedOSError(OSError):
    """We tried to work with an unsupported operating system."""

    def __init__(self) -> None:
        """Initialize the instance."""
        super().__init__(self.msg)

    @property
    def os(self) -> str:
        """The operating system name, from `sys.platform`."""
        return sys.platform

    @property
    def msg(self) -> str:
        """The error message."""
        return (
            f"Cannot run on platform {self.os}. "
            f"Only {_EXPECTED_PLATFORM} is supported."
        )


def ensure_on_macos() -> None:
    """Ensure that we run on MacOS.

    Raises
    ------
    UnsupportedOSError
        When we are not on MacOS (platform: darwin)

    """
    if sys.platform != _EXPECTED_PLATFORM:
        raise UnsupportedOSError


async def run_cmd(*args: str, check: bool = True) -> tuple[
    str, str, int | None
]:
    """Run a system command in an async way.

    Raise
    -----
    CalledProcessError
        The call failed (exit code != 0)
    """
    proc = await asyncio.create_subprocess_exec(
        *args, stdin=None,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = (
        (x.decode().strip() if x else "")
        for x in
        await proc.communicate()
    )
    if check and proc.returncode:
        raise subprocess.CalledProcessError(
            proc.returncode, args, output=stdout, stderr=stderr
        )
    return stdout, stderr, proc.returncode
