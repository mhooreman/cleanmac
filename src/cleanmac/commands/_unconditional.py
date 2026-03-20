"""Unconditional detection/removal."""

import dataclasses
import enum
import pathlib

from cleanmac import logger

from ._abc import ABCCommand


class _EntryKind(enum.Enum):
    FILE = "file"
    DIRECTORY = "directory"


@dataclasses.dataclass(kw_only=True, frozen=True)
class Command(ABCCommand):
    """Unconditional detection/removal of files/directories."""

    paths: tuple[pathlib.Path, ...]
    patterns: tuple[str, ...]
    remove: bool

    def run(self) -> None:
        """Execute the command logic.

        Return
        ------
        True if there was no error.

        """
        for path in self.paths:
            for pattern in self.patterns:
                self._process_case(path, pattern)

    @classmethod
    def _protected_rm(
        cls, candidate: pathlib.Path, entry_kind: _EntryKind
    ) -> None:
        logger.info("Removing %s %s", entry_kind.value, candidate)
        cbs = {
            _EntryKind.FILE: "unlink",
            _EntryKind.DIRECTORY: "rmdir"
        }
        try:
            getattr(candidate, cbs[entry_kind])()
        except OSError as e:
            logger.exception("Cannot remove: %s: %s", candidate, e)

    @classmethod
    def _recurse_remove(cls, match: pathlib.Path) -> None:
        if match.is_file():
            cls._protected_rm(match, _EntryKind.FILE)
            return
        for root, dirs, files in match.walk(top_down=False):
            for name in files:
                cls._protected_rm(root / name, _EntryKind.FILE)
            for name in dirs:
                cls._protected_rm(root / name, _EntryKind.DIRECTORY)

    def _process_case(self, path: pathlib.Path, pattern: str) -> None:
        logger.debug("Searching for %s in %s", pattern, path)
        for match in path.glob(pattern):
            if self.remove:
                self._recurse_remove(match)
            else:
                logger.info("Found %s", match)
