set unstable := true
set script-interpreter := ['uv', 'run', '--script']
set dotenv-load := true

# Default recipe: show available receipes
_default: help

# Provide the list of just receipes; this is called when no receipe if given
help:
    just --list

# Tying verification
types:
    uv run mypy

# Linting, type checking and testing, without fix and halt at first error
qc: lint types testpyver

# Static code analysis/linting. Additional arguments will be passed to ruff check.
lint *args:
    uv run ruff check {{ args }} 

# Run unit tests
test:
    uv run pytest

# Run unit tests with several python versions
testpyver:
    uv run --python 3.13 pytest
    uv run --python 3.14 pytest

# Build
build:
    uv build

# Run the application, passes the additional arguments to it
run *args:
    uv run cleanmac  {{ args }}

# Remove cache files and other temporary files
[script]
clean:
    import pathlib
    import shutil
    import logging

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(message)s'
    )
    logger = logging.getLogger(__name__)

    here = pathlib.Path('.')
    venv = here / '.venv'

    if not venv.exists():
        venv = None
    for case in (
        # We keep .venv as this is always used and costly to build
        "__pycache__", ".mypy_cache", ".coverage", ".pypy_cache", ".DS_Store",
        ".pytest_cache", ".ruff_cache"
    ):
        found = False
        for target in here.glob(f'**/{case}'):
            if venv not in target.parents:
                found = True
                logger.info(f"Removing {target}")
                try:
                    shutil.rmtree(target)
                except NotADirectoryError:
                    target.unlink()
        if not found:
            logger.info(f"No {case} found")

# Clean and then remove dists and .venv
[script]
clobber: clean
    import pathlib
    import shutil
    import logging

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(message)s'
    )
    logger = logging.getLogger(__name__)

    found = False
    for f in (pathlib.Path('.') / "dist").glob("**/*"):
        found = True
        logging.info(f"Removing {f}")
        f.unlink()

    if not found:
        logging.info(f"No dist file found")

    found = False
    for f in pathlib.Path(".").glob("**/.venv"):
        found = True
        logging.info(f"Removing {f}")
        shutil.rmtree(f)

    if not found:
        # Will never happen as uv is called by this justfile and uv creates a
        # .venv
        logging.info(f"No .venv directory")
