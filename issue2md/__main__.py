"""
CLI entry point for issue2md.

This module is executed when running: python -m issue2md
"""

from __future__ import annotations

import sys

from issue2md.cli.parser import parse_args
from issue2md.config.models import Config
from issue2md.cli.run import run


def main() -> int:
    """
    Main entry point for the CLI.

    Returns:
        int: Exit code (0 = success, 1 = failure)
    """
    # Parse command-line arguments
    args = parse_args()

    # Create configuration from environment and arguments
    config = Config.from_args(args)

    # Execute main logic
    return run(config, args.url)


if __name__ == "__main__":
    sys.exit(main())
