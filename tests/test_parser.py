"""
Unit tests for URL parsing.
"""

import unittest

from issue2md.parser.url import (
    parse_github_url,
    ResourceType,
    ParsedURL,
)
from issue2md.github.errors import InvalidURLError, UnsupportedResourceTypeError


class TestParseGitHubURL(unittest.TestCase):
    """URL parsing tests (table-driven)."""

    def test_valid_issue_urls(self):
        """Test valid Issue URLs."""
        test_cases = [
            # (input, expected_type, expected_owner, expected_repo, expected_number)
            ("https://github.com/owner/repo/issues/123",
             ResourceType.ISSUE, "owner", "repo", 123),
            ("https://github.com/foo/bar/issues/1",
             ResourceType.ISSUE, "foo", "bar", 1),
            ("https://github.com/python/cpython/issues/12345",
             ResourceType.ISSUE, "python", "cpython", 12345),
        ]

        for url, exp_type, exp_owner, exp_repo, exp_num in test_cases:
            with self.subTest(url=url):
                result = parse_github_url(url)
                self.assertEqual(result.resource_type, exp_type)
                self.assertEqual(result.owner, exp_owner)
                self.assertEqual(result.repo, exp_repo)
                self.assertEqual(result.number, exp_num)

    def test_valid_pull_request_urls(self):
        """Test valid Pull Request URLs."""
        test_cases = [
            ("https://github.com/owner/repo/pull/456",
             ResourceType.PULL_REQUEST, "owner", "repo", 456),
            ("https://github.com/pulls/repo/pulls/789",
             ResourceType.PULL_REQUEST, "pulls", "repo", 789),
        ]

        for url, exp_type, exp_owner, exp_repo, exp_num in test_cases:
            with self.subTest(url=url):
                result = parse_github_url(url)
                self.assertEqual(result.resource_type, exp_type)
                self.assertEqual(result.owner, exp_owner)
                self.assertEqual(result.repo, exp_repo)
                self.assertEqual(result.number, exp_num)

    def test_valid_discussion_urls(self):
        """Test valid Discussion URLs."""
        test_cases = [
            ("https://github.com/owner/repo/discussions/78",
             ResourceType.DISCUSSION, "owner", "repo", 78),
        ]

        for url, exp_type, exp_owner, exp_repo, exp_num in test_cases:
            with self.subTest(url=url):
                result = parse_github_url(url)
                self.assertEqual(result.resource_type, exp_type)
                self.assertEqual(result.owner, exp_owner)
                self.assertEqual(result.repo, exp_repo)
                self.assertEqual(result.number, exp_num)

    def test_invalid_urls(self):
        """Test invalid URLs."""
        test_cases = [
            "https://example.com/not-github",
            "https://github.com/owner/repo/invalid/123",
            "not-a-url",
            "https://github.com/owner/repo/issues/abc",  # non-numeric
            "https://github.com/owner/repo/",  # incomplete path
        ]

        for url in test_cases:
            with self.subTest(url=url):
                with self.assertRaises((InvalidURLError, UnsupportedResourceTypeError)):
                    parse_github_url(url)


if __name__ == "__main__":
    unittest.main()
