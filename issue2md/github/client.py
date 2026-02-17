"""
GitHub API client for fetching Issues and Pull Requests.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
import requests

from issue2md.github.models import Issue, PullRequest, Comment, Reaction
from issue2md.github.errors import (
    GitHubAPIError,
    ResourceNotFoundError,
    AuthenticationError,
    RateLimitError,
)


class GitHubClient:
    """
    GitHub REST API v3 client.

    This client provides methods to fetch Issues and Pull Requests from GitHub.
    """

    API_BASE_URL = "https://api.github.com"
    ACCEPT_HEADER = "application/vnd.github.v3+json"

    def __init__(self, token: Optional[str] = None) -> None:
        """
        Initialize the GitHub API client.

        Args:
            token: GitHub Personal Access Token (optional)
        """
        self._token = token
        self._session: Optional[requests.Session] = None

    def _get_session(self) -> requests.Session:
        """
        Get or create the HTTP session.

        Returns:
            requests.Session: Configured HTTP session
        """
        if self._session is None:
            self._session = requests.Session()
            if self._token:
                self._session.headers.update({
                    "Authorization": f"Bearer {self._token}",
                    "Accept": self.ACCEPT_HEADER,
                })
            else:
                self._session.headers.update({
                    "Accept": self.ACCEPT_HEADER,
                })
        return self._session

    def fetch_issue(
        self,
        owner: str,
        repo: str,
        number: int,
        include_reactions: bool = False,
    ) -> Issue:
        """
        Fetch an Issue from GitHub.

        Args:
            owner: Repository owner
            repo: Repository name
            number: Issue number
            include_reactions: Whether to include reaction statistics

        Returns:
            Issue: Issue data with comments

        Raises:
            ResourceNotFoundError: If the issue was not found
            AuthenticationError: If authentication fails
            RateLimitError: If the API rate limit is exceeded
            GitHubAPIError: For other API errors
        """
        url = f"{self.API_BASE_URL}/repos/{owner}/{repo}/issues/{number}"

        response = self._request("GET", url)
        data = response.json()

        # Parse reactions if requested
        reactions = self._parse_reactions(data.get("reactions", {})) if include_reactions else Reaction()

        # Parse comments
        comments_url = data["comments_url"]
        comments = self._fetch_comments(comments_url, include_reactions)

        # Determine status
        status = "closed" if data.get("state") == "closed" else "open"

        return Issue(
            number=data["number"],
            title=data["title"],
            author=data["user"]["login"],
            author_url=data["user"]["html_url"],
            created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00")),
            status=status,  # type: ignore
            body=data.get("body", "") or "",
            comments=comments,
            labels=[label["name"] for label in data.get("labels", [])],
            reactions=reactions,
        )

    def fetch_pull_request(
        self,
        owner: str,
        repo: str,
        number: int,
        include_reactions: bool = False,
    ) -> PullRequest:
        """
        Fetch a Pull Request from GitHub.

        Args:
            owner: Repository owner
            repo: Repository name
            number: PR number
            include_reactions: Whether to include reaction statistics

        Returns:
            PullRequest: PR data with comments and review comments

        Raises:
            ResourceNotFoundError: If the PR was not found
            AuthenticationError: If authentication fails
            RateLimitError: If the API rate limit is exceeded
            GitHubAPIError: For other API errors
        """
        url = f"{self.API_BASE_URL}/repos/{owner}/{repo}/pulls/{number}"

        response = self._request("GET", url)
        data = response.json()

        # Parse status
        if data.get("merged_at"):
            status = "merged"
        elif data.get("state") == "closed":
            status = "closed"
        else:
            status = "open"

        # Fetch regular comments
        comments_url = f"{self.API_BASE_URL}/repos/{owner}/{repo}/issues/{number}/comments"
        regular_comments = self._fetch_comments(comments_url, include_reactions)

        # Fetch review comments
        review_comments_url = f"{self.API_BASE_URL}/repos/{owner}/{repo}/pulls/{number}/comments"
        review_comments = self._fetch_review_comments(review_comments_url, include_reactions)

        # Merge and sort by created_at
        all_comments = regular_comments + review_comments
        all_comments.sort(key=lambda c: c.created_at)

        return PullRequest(
            number=data["number"],
            title=data["title"],
            author=data["user"]["login"],
            author_url=data["user"]["html_url"],
            created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00")),
            status=status,  # type: ignore
            body=data.get("body", "") or "",
            comments=all_comments,
            labels=[label["name"] for label in data.get("labels", [])],
        )

    def _fetch_comments(
        self,
        url: str,
        include_reactions: bool,
    ) -> list[Comment]:
        """
        Fetch comments from a URL.

        Args:
            url: Comments API URL
            include_reactions: Whether to include reaction statistics

        Returns:
            list[Comment]: List of comments
        """
        response = self._request("GET", url)
        data = response.json()

        # Handle single comment vs list
        if not isinstance(data, list):
            data = [data]

        comments = []
        for comment_data in data:
            reactions = self._parse_reactions(
                comment_data.get("reactions", {})
            ) if include_reactions else Reaction()

            comment = Comment(
                id=comment_data["id"],
                author=comment_data["user"]["login"],
                author_url=comment_data["user"]["html_url"],
                created_at=datetime.fromisoformat(comment_data["created_at"].replace("Z", "+00:00")),
                updated_at=datetime.fromisoformat(comment_data["updated_at"].replace("Z", "+00:00")),
                body=comment_data.get("body", "") or "",
                reactions=reactions,
            )
            comments.append(comment)

        return comments

    def _fetch_review_comments(
        self,
        url: str,
        include_reactions: bool,
    ) -> list[Comment]:
        """
        Fetch PR review comments from a URL.

        Args:
            url: Review comments API URL
            include_reactions: Whether to include reaction statistics

        Returns:
            list[Comment]: List of review comments
        """
        response = self._request("GET", url)
        data = response.json()

        # Handle single comment vs list
        if not isinstance(data, list):
            data = [data]

        comments = []
        for comment_data in data:
            reactions = self._parse_reactions(
                comment_data.get("reactions", {})
            ) if include_reactions else Reaction()

            comment = Comment(
                id=comment_data["id"],
                author=comment_data["user"]["login"],
                author_url=comment_data["user"]["html_url"],
                created_at=datetime.fromisoformat(comment_data["created_at"].replace("Z", "+00:00")),
                updated_at=datetime.fromisoformat(comment_data["updated_at"].replace("Z", "+00:00")),
                body=comment_data.get("body", "") or "",
                reactions=reactions,
                is_review_comment=True,
                review_file_path=comment_data.get("path"),
                review_line=comment_data.get("line"),
            )
            comments.append(comment)

        return comments

    def _parse_reactions(self, reactions_data: dict) -> Reaction:
        """
        Parse reaction data from API response.

        Args:
            reactions_data: Raw reactions data from API

        Returns:
            Reaction: Parsed reaction statistics
        """
        return Reaction(
            thumbs_up=reactions_data.get("+1", 0) + reactions_data.get("thumbs_up", 0),
            thumbs_down=reactions_data.get("-1", 0) + reactions_data.get("thumbs_down", 0),
            laugh=reactions_data.get("laugh", 0),
            hooray=reactions_data.get("hooray", 0),
            confused=reactions_data.get("confused", 0),
            heart=reactions_data.get("heart", 0),
            rocket=reactions_data.get("rocket", 0),
            eyes=reactions_data.get("eyes", 0),
        )

    def _request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        Send an HTTP request to the GitHub API.

        Args:
            method: HTTP method
            url: Request URL
            **kwargs: Additional arguments for requests

        Returns:
            requests.Response: API response

        Raises:
            ResourceNotFoundError: If status code is 404
            AuthenticationError: If status code is 401
            RateLimitError: If status code is 403
            GitHubAPIError: For other error status codes
        """
        session = self._get_session()
        response = session.request(method, url, **kwargs)

        if response.status_code == 404:
            raise ResourceNotFoundError(response_text=response.text)
        elif response.status_code == 401:
            raise AuthenticationError(response_text=response.text)
        elif response.status_code == 403:
            raise RateLimitError(response_text=response.text)
        elif not response.ok:
            raise GitHubAPIError(
                message=f"API request failed: {response.status_code}",
                status_code=response.status_code,
                response_text=response.text,
            )

        return response

    def close(self) -> None:
        """Close the HTTP session."""
        if self._session:
            self._session.close()
            self._session = None

    def __enter__(self) -> GitHubClient:
        return self

    def __exit__(self, *args) -> None:
        self.close()
