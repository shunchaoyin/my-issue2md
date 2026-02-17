"""
Command-line argument parsing for issue2md.
"""

from __future__ import annotations

import argparse
from typing import Optional


def parse_args(args: Optional[list[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments.

    Args:
        args: List of argument strings, None to use sys.argv[1:]

    Returns:
        argparse.Namespace: Parsed arguments

    Raises:
        SystemExit: If arguments are invalid (exit code 2)
    """
    parser = argparse.ArgumentParser(
        prog="issue2md",
        description="Convert GitHub Issues/PRs/Discussions to Markdown",
    )

    # Positional argument: URL
    parser.add_argument(
        "url",
        help="GitHub Issue/PR/Discussion URL",
    )

    # Optional positional argument: output file
    parser.add_argument(
        "output_file",
        nargs="?",
        default=None,
        help="Output file path (default: stdout)",
    )

    # Flags
    parser.add_argument(
        "-enable-reactions",
        action="store_true",
        help="Include reaction statistics",
    )

    parser.add_argument(
        "-enable-user-links",
        action="store_true",
        help="Render usernames as links to GitHub profiles",
    )

    return parser.parse_args(args)
