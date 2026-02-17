"""
Configuration management for issue2md.

Config is immutable and created from environment variables and/or command-line arguments.
"""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Config:
    """
    Immutable configuration for issue2md.

    Attributes:
        github_token: GitHub Personal Access Token (from GITHUB_TOKEN env var)
        enable_reactions: Whether to include reaction statistics
        enable_user_links: Whether to render usernames as links
        output_file: Output file path (None = stdout)
    """

    # GitHub authentication
    github_token: Optional[str] = None

    # Feature flags
    enable_reactions: bool = False
    enable_user_links: bool = False

    # Output settings
    output_file: Optional[str] = None  # None = stdout

    @classmethod
    def from_env(cls) -> Config:
        """
        Create a Config instance from environment variables.

        Returns:
            Config: Configuration with values from environment
        """
        return cls(
            github_token=os.getenv("GITHUB_TOKEN"),
        )

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> Config:
        """
        Create a Config instance from parsed command-line arguments.

        Environment variables are used as defaults, then overridden by args.

        Args:
            args: Parsed command-line arguments from argparse

        Returns:
            Config: Configuration with values from environment and arguments
        """
        base = cls.from_env()
        return cls(
            github_token=base.github_token,
            enable_reactions=args.enable_reactions,
            enable_user_links=args.enable_user_links,
            output_file=args.output_file,
        )
