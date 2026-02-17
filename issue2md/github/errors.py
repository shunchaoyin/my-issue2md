"""
Custom exception classes for issue2md.

All exceptions inherit from Issue2MDError for consistent error handling.
"""

from __future__ import annotations


class Issue2MDError(Exception):
    """Base exception for all issue2md errors."""

    pass


class InvalidURLError(Issue2MDError):
    """Raised when the URL format is invalid or not a GitHub URL."""

    pass


class UnsupportedResourceTypeError(Issue2MDError):
    """Raised when the resource type is not supported."""

    pass


class GitHubAPIError(Issue2MDError):
    """
    Base exception for GitHub API errors.

    Attributes:
        status_code: HTTP status code from the API response
        response_text: Raw response text from the API
    """

    def __init__(self, message: str, status_code: int, response_text: str) -> None:
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(message)


class ResourceNotFoundError(GitHubAPIError):
    """Raised when the requested resource was not found (404)."""

    def __init__(self, message: str = "Resource not found", response_text: str = "") -> None:
        super().__init__(message, 404, response_text)


class AuthenticationError(GitHubAPIError):
    """Raised when authentication fails (401)."""

    def __init__(self, message: str = "Authentication failed", response_text: str = "") -> None:
        super().__init__(message, 401, response_text)


class RateLimitError(GitHubAPIError):
    """Raised when the GitHub API rate limit is exceeded (403)."""

    def __init__(self, message: str = "API rate limit exceeded", response_text: str = "") -> None:
        super().__init__(message, 403, response_text)
