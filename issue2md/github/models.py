"""
Data models for GitHub resources.

All models are frozen dataclasses to ensure immutability.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, Optional, List


# ============================================================================
# Base Types
# ============================================================================


@dataclass(frozen=True)
class Reaction:
    """
    Reaction statistics for a comment or issue.

    Attributes:
        thumbs_up: +1 reactions
        thumbs_down: -1 reactions
        laugh: laugh reactions
        hooray: hooray reactions
        confused: confused reactions
        heart: heart reactions
        rocket: rocket reactions
        eyes: eyes reactions
    """

    thumbs_up: int = 0
    thumbs_down: int = 0
    laugh: int = 0
    hooray: int = 0
    confused: int = 0
    heart: int = 0
    rocket: int = 0
    eyes: int = 0


@dataclass(frozen=True)
class Comment:
    """
    A comment or reply on an Issue/PR/Discussion.

    Attributes:
        id: Comment ID
        author: Username of the author
        author_url: URL to the author's GitHub profile
        created_at: Creation timestamp
        updated_at: Last update timestamp
        body: Comment body content (Markdown)
        reactions: Reaction statistics
        replies: Nested replies (in chronological order)
        is_review_comment: Whether this is a PR review comment
        review_file_path: File path for PR review comments
        review_line: Line number for PR review comments
        is_answer: Whether this is the accepted answer (Discussion only)
    """

    id: int
    author: str
    author_url: str
    created_at: datetime
    updated_at: datetime
    body: str
    reactions: Reaction = field(default_factory=Reaction)

    # Nested replies (in chronological order)
    replies: List[Comment] = field(default_factory=list)

    # PR Review Comment specific fields
    is_review_comment: bool = False
    review_file_path: Optional[str] = None
    review_line: Optional[int] = None

    # Discussion specific field
    is_answer: bool = False


# ============================================================================
# Resource Types
# ============================================================================


@dataclass(frozen=True)
class Issue:
    """
    GitHub Issue data.

    Attributes:
        number: Issue number
        title: Issue title
        author: Username of the author
        author_url: URL to the author's GitHub profile
        created_at: Creation timestamp
        updated_at: Last update timestamp
        status: Issue status ("open" or "closed")
        body: Issue body content (Markdown)
        comments: List of comments (in chronological order)
        labels: List of label names
        reactions: Reaction statistics
    """

    number: int
    title: str
    author: str
    author_url: str
    created_at: datetime
    updated_at: datetime
    status: Literal["open", "closed"]
    body: str
    comments: List[Comment] = field(default_factory=list)
    labels: List[str] = field(default_factory=list)
    reactions: Reaction = field(default_factory=Reaction)


@dataclass(frozen=True)
class PullRequest:
    """
    GitHub Pull Request data.

    Attributes:
        number: PR number
        title: PR title
        author: Username of the author
        author_url: URL to the author's GitHub profile
        created_at: Creation timestamp
        updated_at: Last update timestamp
        status: PR status ("open", "closed", or "merged")
        body: PR body content (Markdown)
        comments: List of comments and review comments (in chronological order)
        labels: List of label names
    """

    number: int
    title: str
    author: str
    author_url: str
    created_at: datetime
    updated_at: datetime
    status: Literal["open", "closed", "merged"]
    body: str
    comments: List[Comment] = field(default_factory=list)
    labels: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class Discussion:
    """
    GitHub Discussion data.

    Attributes:
        number: Discussion number
        title: Discussion title
        author: Username of the author
        author_url: URL to the author's GitHub profile
        created_at: Creation timestamp
        updated_at: Last update timestamp
        status: Discussion status ("open" or "closed")
        body: Discussion body content (Markdown)
        comments: List of comments (in chronological order)
    """

    number: int
    title: str
    author: str
    author_url: str
    created_at: datetime
    updated_at: datetime
    status: Literal["open", "closed"]
    body: str
    comments: List[Comment] = field(default_factory=list)


# Union type for all resource types
GitHubResource = Issue | PullRequest | Discussion
