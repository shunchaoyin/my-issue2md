"""
Main execution logic for issue2md.
"""

from __future__ import annotations

import sys
from typing import Optional, TextIO

from issue2md.cli.parser import parse_args
from issue2md.config.models import Config
from issue2md.github.errors import (
    Issue2MDError,
    InvalidURLError,
    GitHubAPIError,
    ResourceNotFoundError,
    AuthenticationError,
    RateLimitError,
)
from issue2md.github import GitHubClient
from issue2md.parser import parse_github_url, ParsedURL, ResourceType
from issue2md.converter import convert_to_markdown


def run(config: Config, url: str) -> int:
    """
    Main execution function.

    Args:
        config: Configuration object
        url: GitHub URL to convert

    Returns:
        int: Exit code (0 = success, 1 = failure)
    """
    try:
        # Step 1: Parse URL
        parsed: ParsedURL = parse_github_url(url)

        # Step 2: Fetch resource from GitHub
        with GitHubClient(token=config.github_token) as client:
            if parsed.resource_type == ResourceType.ISSUE:
                resource = client.fetch_issue(
                    owner=parsed.owner,
                    repo=parsed.repo,
                    number=parsed.number,
                    include_reactions=config.enable_reactions,
                )
            elif parsed.resource_type == ResourceType.PULL_REQUEST:
                resource = client.fetch_pull_request(
                    owner=parsed.owner,
                    repo=parsed.repo,
                    number=parsed.number,
                    include_reactions=config.enable_reactions,
                )
            else:
                # Discussion support not implemented yet
                print(f"Error: Discussion support is not yet implemented", file=sys.stderr)
                return 1

        # Step 3: Convert to Markdown
        with _open_output(config.output_file) as output:
            convert_to_markdown(resource, config, output, url=parsed.original_url)

        return 0

    except InvalidURLError as e:
        print(f"Error: Invalid URL format - {e}", file=sys.stderr)
        return 1
    except ResourceNotFoundError as e:
        print(f"Error: Resource not found - {e}", file=sys.stderr)
        return 1
    except AuthenticationError:
        print("Error: Private repository. Please set GITHUB_TOKEN environment variable", file=sys.stderr)
        return 1
    except RateLimitError as e:
        print(f"Error: GitHub API rate limit exceeded - {e}", file=sys.stderr)
        return 1
    except GitHubAPIError as e:
        print(f"Error: GitHub API error ({e.status_code}) - {e}", file=sys.stderr)
        return 1
    except (IOError, OSError) as e:
        print(f"Error: Cannot write to file - {e}", file=sys.stderr)
        return 1
    except Issue2MDError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        # Catch unexpected exceptions
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def _open_output(output_file: Optional[str]) -> TextIO:
    """
    Open output file or return stdout.

    Args:
        output_file: Output file path, None for stdout

    Returns:
        TextIO: File object or stdout
    """
    if output_file is None:
        return sys.stdout
    return open(output_file, "w", encoding="utf-8")
