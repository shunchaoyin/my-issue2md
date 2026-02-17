"""
URL parsing and resource type detection.
"""

from issue2md.parser.url import (
    ResourceType,
    ParsedURL,
    parse_github_url,
)

__all__ = [
    "ResourceType",
    "ParsedURL",
    "parse_github_url",
]
