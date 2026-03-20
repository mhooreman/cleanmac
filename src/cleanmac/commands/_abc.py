"""Abstract base classes for commands."""

import abc
import dataclasses

from cleanmac import logger


@dataclasses.dataclass(kw_only=True, frozen=True)
class ABCCommand(abc.ABC):
    """Abstract base class for command.

    This provides callable instances, which calls (abstract) `self.run()`.
    """

    def __call__(self) -> None:
        """Execute the command as a callable instance."""
        logger.info("Starting %s.%s", type(self).__module__, self)
        self.run()
        logger.info(
            "Completed %s.%s", type(self).__module__, type(self).__name__
        )

    @abc.abstractmethod
    def run(self) -> None:
        """Execute the command logic."""
