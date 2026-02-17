"""
CLI entry point for issue2md.

This module is the main entry point when running: python -m cmd.issue2md
"""

from issue2md.__main__ import main

if __name__ == "__main__":
    import sys
    sys.exit(main())
