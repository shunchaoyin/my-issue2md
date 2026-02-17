"""
URL parsing and resource type detection for GitHub URLs.

This module provides utilities to parse GitHub URLs and identify the resource type.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlparse

from issue2md.github.errors import InvalidURLError, UnsupportedResourceTypeError


class ResourceType(Enum):
    """GitHub resource type."""

    ISSUE = "issue"
    PULL_REQUEST = "pull_request"
    DISCUSSION = "discussion"


@dataclass(frozen=True)
class ParsedURL:
    """
    Parsed GitHub URL.

    Attributes:
        resource_type: The type of GitHub resource
        owner: Repository owner
        repo: Repository name
        number: Issue/PR/Discussion number
        original_url: The original URL string
    """

    resource_type: ResourceType
    owner: str
    repo: str
    number: int
    original_url: str


def parse_github_url(url: str) -> ParsedURL:
    """
    Parse a GitHub URL and identify the resource type.

    Supported URL formats:
    - Issue:      https://github.com/{owner}/{repo}/issues/{number}
    - Pull:       https://github.com/{owner}/{repo}/pull/{number}
    - Discussion: https://github.com/{owner}/{repo}/discussions/{number}

    Args:
        url: GitHub URL for an Issue, PR, or Discussion

    Returns:
        ParsedURL: Parsed URL information

    Raises:
        InvalidURLError: If the URL format is invalid
        UnsupportedResourceTypeError: If the resource type is not supported

    Examples:
        >>> parse_github_url("https://github.com/owner/repo/issues/123")
        ParsedURL(resource_type=ResourceType.ISSUE, owner='owner', repo='repo', number=123, ...)
    """
    # Parse the URL
    try:
        parsed = urlparse(url)
    except Exception as e:
        raise InvalidURLError(f"Invalid URL: {e}") from e

    # Validate domain
    if parsed.netloc != "github.com":
        raise InvalidURLError(
            f"Invalid URL: expected github.com, got {parsed.netloc}"
        )

    # Parse path: /{owner}/{repo}/{type}/{number}
    parts = parsed.path.strip("/").split("/")

    if len(parts) < 4:
        raise InvalidURLError(
            f"Invalid URL path: expected /owner/repo/type/number, got /{parsed.path}"
        )

    owner, repo, resource_type_str, number_str = parts[0], parts[1], parts[2], parts[3]

    # Validate number is an integer
    try:
        number = int(number_str)
    except ValueError as e:
        raise InvalidURLError(
            f"Invalid URL: expected number, got '{number_str}'"
        ) from e

    # Identify resource type
    resource_type = _identify_resource_type(resource_type_str)

    return ParsedURL(
        resource_type=resource_type,
        owner=owner,
        repo=repo,
        number=number,
        original_url=url,
    )


def _identify_resource_type(type_str: str) -> ResourceType:
    """
    Map URL path segment to ResourceType enum.

    Args:
        type_str: The type segment from the URL path (e.g., "issues", "pull")

    Returns:
        ResourceType: The corresponding resource type

    Raises:
        UnsupportedResourceTypeError: If the type is not supported
    """
    type_mapping = {
        "issues": ResourceType.ISSUE,
        "issue": ResourceType.ISSUE,
        "pull": ResourceType.PULL_REQUEST,
        "pulls": ResourceType.PULL_REQUEST,
        "discussions": ResourceType.DISCUSSION,
        "discussion": ResourceType.DISCUSSION,
    }

    if type_str not in type_mapping:
        raise UnsupportedResourceTypeError(
            f"Unsupported resource type: '{type_str}'. "
            f"Supported types: issue, pull, discussion"
        )

    return type_mapping[type_str]
