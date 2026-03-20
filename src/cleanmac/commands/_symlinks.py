"""Symbolic links cleanup."""

import dataclasses
import pathlib

from cleanmac import logger

from ._abc import ABCCommand


@dataclasses.dataclass(kw_only=True, frozen=True)
class Command(ABCCommand):
    """Detection and cleaning of dead symbolic links.

    Note
    ----
    If `p=pathlib.Path(...` correponds to a broken symbolic link, then
    `(p.is_symlink() and not p.exists()` is `True`.

    """

    paths: tuple[pathlib.Path, ...]
    remove: bool

    def run(self) -> None:
        """Execute the command logic."""
        for path in self.paths:
            self._process_case(path)

    def _process_case(self, path: pathlib.Path) -> None:
        logger.debug("Processing %s", path)
        for match in path.glob("**/*"):
            if match.is_symlink():
                if not match.exists():
                    msg = "Removing" if self.remove else "Found"
                    msg += " broken link: %s"
                    logger.info(msg, match)
                if self.remove:
                    try:
                        match.unlink()
                    except OSError as e:
                        logger.exception("Cannot remove: %s: %s", match, e)
