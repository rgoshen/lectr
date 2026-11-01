"""Command-line entry point."""

import argparse
from collections.abc import Sequence

from lectr import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lectr",
        description="Turn DRM-free e-books into audiobooks with a local text-to-speech model.",
    )
    parser.add_argument("--version", action="version", version=f"lectr {__version__}")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    build_parser().parse_args(argv)
    return 0
