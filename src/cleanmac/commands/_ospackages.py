"""Detection/removal of registered OS packages which has disappeared."""

from __future__ import annotations

import asyncio
import dataclasses
import enum
import functools
import pathlib
import subprocess  # noqa: S404

from cleanmac import logger

from ._abc import ABCCommand


class _EntryKind(enum.Enum):
    FILE = "file"
    DIRECTORY = "directory"


async def _run_cmd(*args: str, check: bool = True) -> tuple[
    bytes, bytes, int | None
]:
    proc = await asyncio.create_subprocess_exec(
        *args, stdin=None,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    if check and proc.returncode:
        raise subprocess.CalledProcessError(
            proc.returncode, args, output=stdout, stderr=stderr
        )
    return stdout, stderr, proc.returncode


class _PackageParsingError(Exception):
    def __init__(self, package: _Package) -> None:
        self._package = package
        super().__init__(self.msg)

    @property
    def name(self) -> str:
        return self.package.name

    @property
    def package(self) -> _Package:
        return self._package

    @property
    def msg(self) -> str:
        return self.name


class UnknownLocationError(_PackageParsingError):
    pass


class UnknownVolumeError(_PackageParsingError):
    pass


class UnsupportedVolumeError(_PackageParsingError):
    pass


class _Package:
    def __init__(self, name: str) -> None:
        self._name = name
        self._content: tuple[pathlib.Path, ...] | None = None
        self._parsing_status: bool | None = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def parsing_status(self) -> bool:
        if self._parsing_status is None:
            msg = "Parsing status not known yet"
            raise RuntimeError(msg)
        return self._parsing_status

    @parsing_status.setter
    def parsing_status(self, status: bool) -> None:
        self._parsing_status = status

    @property
    def content(self) -> tuple[pathlib.Path, ...]:
        if self._content is None:
            msg = f"Content not loaded yet. Run (async) {self.load_content}"
            raise RuntimeError(msg)
        return self._content

    async def load_content(self) -> None:
        status = True
        try:
            location = await self._get_location()
            logger.debug("Listing content of %s", self.name)
            stdout, *_ = await _run_cmd("pkgutil", "--files", self.name)
            [x for x in stdout.decode().split("\n") if x]
            pathlib.Path("/")
            self._content = tuple(
                location / f for f in sorted(
                    stdout.decode().split("\n")
                ) if f
            )
            self._content = tuple(
                # Directories are making false positivites and might drop
                # system directories (/usr/local, etc.)
                f for f in self._content if not f.is_dir()
            )
        except _PackageParsingError as e:
            status = False
            msg = f"Error while parsing {self.name}: {e}"
            logger.exception(msg)
        finally:
            self.parsing_status = status

    async def _get_location(self) -> pathlib.Path:
        logger.debug("Loading location of %s", self.name)
        stdout, *_ = await _run_cmd("pkgutil", "--info", self.name)
        volume: str | None = None
        location: str | None = None
        for ln in stdout.decode().split("\n"):
            if ":" not in ln:
                continue
            k, v = [x.strip() for x in ln.split(":")]
            if k == "volume":
                volume = v
                volume = v.strip()
                if not volume:
                    volume = None
                continue
            if k == "location":
                location = v.strip()
                if not location:
                    location = None
                continue
        if volume is None:
            raise UnknownVolumeError(self)
        if location is None:
            raise UnknownLocationError(self)
        if volume != "/":
            raise UnsupportedVolumeError(self)
        return pathlib.Path(location)

    @property
    def all_exists(self) -> bool:
        # We avoid all([...]) because that would evaluate everything
        # (performance gain is big)
        if not self.parsing_status:
            msg = "Cannot proceed: parsing failed"
            raise RuntimeError(msg)
        return all(f.exists() for f in self.content)

    @property
    def none_exists(self) -> bool:
        # We avoid all([...]) because that would evaluate everything
        # (performance gain is big)
        if not self.parsing_status:
            msg = "Cannot proceed: parsing failed"
            raise RuntimeError(msg)
        return all(not f.exists() for f in self.content)

    @property
    def missing_files(self) -> tuple[pathlib.Path, ...]:
        return tuple(f for f in self.content if not f.exists())

    @property
    def existing_files(self) -> tuple[pathlib.Path, ...]:
        return tuple(f for f in self.content if f.exists())


@dataclasses.dataclass(kw_only=True, frozen=True)
class Command(ABCCommand):
    """Detection/removal of registered OS packages which has disappeared.

    Apple packages are excluded.
    """

    remove: bool

    def run(self) -> None:
        """Execute the command logic."""
        logger.info("TODO %s", self)
        _ = self._packages  # lazy loading
        self._load_packages_contents()
        self._process_packages()

    def _load_packages_contents(self) -> None:
        async def _aload() -> None:
            tasks = [p.load_content() for p in self._packages]
            await(asyncio.gather(*tasks))
        asyncio.run(_aload())

    @functools.cached_property
    def _packages(self) -> tuple[_Package, ...]:
        stdout, *_ = asyncio.run(_run_cmd("pkgutil", "--packages"))
        ret = tuple(
            _Package(x) for x in sorted(stdout.decode().split("\n")) if x
        )
        return tuple(p for p in ret if not p.name.startswith("com.apple"))

    def _process_packages(self) -> None:
        for p in self._packages:
            if not p.parsing_status:
                logger.warning("Parsing of %s failed. Skipping.", p.name)
                continue
            if p.none_exists:
                if self.remove:
                    logger.info("Forgetting uninstalled package %s", p.name)
                    _, stderr, _ = asyncio.run(
                        _run_cmd("pkgutil", "--forget", p.name)
                    )
                    if stderr:
                        # exit code is 0 even in case of issue
                        logger.error(
                            "Error while processing: %s",
                            stderr.decode().strip()
                        )
                else:
                    logger.info("Found uninstalled package %s", p.name)
                continue
            if not p.all_exists:
                m = "Missing:" + "".join(
                    f"\n    - {x}" for x in p.missing_files
                )
                e = "Existing:" + "".join(
                    f"\n    - {x}" for x in p.existing_files
                )
                logger.warning(
                    "%s seems to have missing files:\n%s\n%s", p.name, m, e
                )
                logger.warning(
                    "No decision on %s. Use pkgutil --forget %s if you want "
                    "to forget it.", p.name, p.name
                )
