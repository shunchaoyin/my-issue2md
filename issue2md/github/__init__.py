"""
GitHub API client and data models.
"""

from issue2md.github.models import (
    Reaction,
    Comment,
    Issue,
    PullRequest,
    Discussion,
    GitHubResource,
)
from issue2md.github.errors import (
    Issue2MDError,
    InvalidURLError,
    UnsupportedResourceTypeError,
    GitHubAPIError,
    ResourceNotFoundError,
    AuthenticationError,
    RateLimitError,
)
from issue2md.github.client import GitHubClient

__all__ = [
    # Models
    "Reaction",
    "Comment",
    "Issue",
    "PullRequest",
    "Discussion",
    "GitHubResource",
    # Errors
    "Issue2MDError",
    "InvalidURLError",
    "UnsupportedResourceTypeError",
    "GitHubAPIError",
    "ResourceNotFoundError",
    "AuthenticationError",
    "RateLimitError",
    # Client
    "GitHubClient",
]
