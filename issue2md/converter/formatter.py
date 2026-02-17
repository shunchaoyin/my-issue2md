"""
Markdown formatter for converting GitHub resources to Markdown.
"""

from __future__ import annotations

from datetime import datetime
from typing import TextIO

from issue2md.config.models import Config
from issue2md.github.models import (
    GitHubResource,
    Issue,
    PullRequest,
    Discussion,
    Comment,
    Reaction,
)


def convert_to_markdown(
    resource: GitHubResource,
    config: Config,
    output: TextIO,
    url: str | None = None,
) -> None:
    """
    Convert a GitHub resource to Markdown and write to output.

    Args:
        resource: GitHub resource (Issue, PR, or Discussion)
        config: Configuration object
        output: Output stream (file or stdout)
        url: Original GitHub URL (for source link)

    Raises:
        IOError: If writing fails
    """
    # Use provided URL or generate from resource
    source_url = url if url else _get_source_url(resource)

    # Generate YAML Frontmatter
    frontmatter = _render_frontmatter(resource, source_url)

    # Generate body
    body = _render_body(resource, config.enable_user_links)

    # Generate comments section
    comments = _render_comments(
        resource.comments,
        config.enable_user_links,
        config.enable_reactions,
    )

    # Write to output
    output.write(frontmatter)
    output.write("\n")
    output.write(body)
    output.write("\n")
    output.write(comments)
    output.write("\n---\n\n")
    output.write(f"**生成于:** issue2md v0.1.0 | **来源:** {source_url}\n")


# ============================================================================
# Internal helper functions
# ============================================================================


def _render_frontmatter(resource: GitHubResource, source_url: str) -> str:
    """Generate YAML Frontmatter for the resource."""
    lines = ["---"]

    # Basic fields
    resource_type = _get_resource_type_string(resource)
    lines.append(f'title: "[{resource_type} #{resource.number}] {resource.title}"')
    lines.append(f'url: "{source_url}"')
    lines.append(f'type: "{resource_type}"')
    lines.append(f"number: {resource.number}")
    lines.append(f'author: "{resource.author}"')
    lines.append(f'author_url: "{resource.author_url}"')
    lines.append(f'created_at: "{_format_datetime(resource.created_at)}"')
    lines.append(f'updated_at: "{_format_datetime(resource.updated_at)}"')
    lines.append(f'status: "{resource.status}"')

    # Labels (Issue/PR only)
    if hasattr(resource, "labels") and resource.labels:
        labels_str = '", "'.join(resource.labels)
        lines.append(f'labels: ["{labels_str}"]')

    # Reactions (Issue only)
    if hasattr(resource, "reactions") and any([
        resource.reactions.thumbs_up,
        resource.reactions.thumbs_down,
        resource.reactions.laugh,
        resource.reactions.hooray,
        resource.reactions.confused,
        resource.reactions.heart,
        resource.reactions.rocket,
        resource.reactions.eyes,
    ]):
        lines.append("reactions:")
        if resource.reactions.thumbs_up:
            lines.append(f"  thumbs_up: {resource.reactions.thumbs_up}")
        if resource.reactions.thumbs_down:
            lines.append(f"  thumbs_down: {resource.reactions.thumbs_down}")
        if resource.reactions.laugh:
            lines.append(f"  laugh: {resource.reactions.laugh}")
        if resource.reactions.hooray:
            lines.append(f"  hooray: {resource.reactions.hooray}")
        if resource.reactions.confused:
            lines.append(f"  confused: {resource.reactions.confused}")
        if resource.reactions.heart:
            lines.append(f"  heart: {resource.reactions.heart}")
        if resource.reactions.rocket:
            lines.append(f"  rocket: {resource.reactions.rocket}")
        if resource.reactions.eyes:
            lines.append(f"  eyes: {resource.reactions.eyes}")

    lines.append("---")
    return "\n".join(lines)


def _render_body(resource: GitHubResource, enable_user_links: bool) -> str:
    """Generate the body section of the Markdown."""
    resource_type = _get_resource_type_string(resource)
    author_formatted = _format_user_link(resource.author, enable_user_links)

    lines = [
        f"# [{resource_type} #{resource.number}] {resource.title}",
        "",
        f"**作者:** {author_formatted} | **创建时间:** {_format_datetime(resource.created_at)} UTC | **状态:** {resource.status.capitalize()}",
    ]

    # Labels (Issue/PR only)
    if hasattr(resource, "labels") and resource.labels:
        labels_str = ", ".join(resource.labels)
        lines.append(f"**标签:** {labels_str}")

    lines.extend(["", "---", "", "## 描述", "", resource.body if resource.body else "*No description.*", ""])

    return "\n".join(lines)


def _render_comments(
    comments: list[Comment],
    enable_user_links: bool,
    enable_reactions: bool,
    indent_level: int = 0,
) -> str:
    """Generate the comments section."""
    if not comments:
        return ""

    lines = ["## 评论 (按时间正序)", ""]

    for comment in comments:
        lines.extend(_render_single_comment(comment, enable_user_links, enable_reactions, indent_level))

        # Render nested replies
        if comment.replies:
            for reply in comment.replies:
                lines.extend(_render_single_comment(reply, enable_user_links, enable_reactions, indent_level + 1))

    return "\n".join(lines)


def _render_single_comment(
    comment: Comment,
    enable_user_links: bool,
    enable_reactions: bool,
    indent_level: int = 0,
) -> list[str]:
    """Render a single comment."""
    author_formatted = _format_user_link(comment.author, enable_user_links)
    timestamp = _format_datetime(comment.created_at)

    # Build header
    header = f"### {author_formatted} ({timestamp} UTC)"

    # Add suffixes
    suffixes = []
    if comment.is_review_comment:
        suffixes.append("[Review Comment]")
    if comment.is_answer:
        suffixes.append("✅ [Accepted Answer]")
    if suffixes:
        header += " " + " ".join(suffixes)

    lines = [header, ""]

    # Add review comment file path
    if comment.is_review_comment and comment.review_file_path:
        lines.append(f"**File:** `{comment.review_file_path}:{comment.review_line}`")
        lines.append("")

    # Add body
    lines.append(comment.body if comment.body else "*No content.*")
    lines.append("")

    # Add reactions
    if enable_reactions and any([
        comment.reactions.thumbs_up,
        comment.reactions.thumbs_down,
        comment.reactions.laugh,
        comment.reactions.hooray,
        comment.reactions.confused,
        comment.reactions.heart,
        comment.reactions.rocket,
        comment.reactions.eyes,
    ]):
        reactions_str = _format_reactions(comment.reactions)
        lines.append(f"**Reactions:** {reactions_str}")
        lines.append("")

    # Apply indentation for nested replies
    if indent_level > 0:
        indent = "> " * indent_level
        lines = [indent + line if line else "" for line in lines]

    return lines


def _format_user_link(username: str, enabled: bool) -> str:
    """Format a username as a link if enabled."""
    if enabled:
        return f"[@{username}](https://github.com/{username})"
    return f"@{username}"


def _format_datetime(dt: datetime) -> str:
    """Format a datetime as ISO 8601 UTC string."""
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _format_reactions(reactions: Reaction) -> str:
    """Format reactions as a string."""
    parts = []
    emoji_map = {
        "thumbs_up": "👍",
        "thumbs_down": "👎",
        "laugh": "😄",
        "hooray": "🎉",
        "confused": "😕",
        "heart": "❤️",
        "rocket": "🚀",
        "eyes": "👀",
    }

    for key, emoji in emoji_map.items():
        count = getattr(reactions, key, 0)
        if count > 0:
            parts.append(f"{emoji} {count}")

    return ", ".join(parts) if parts else ""


def _get_resource_type_string(resource: GitHubResource) -> str:
    """Get the resource type string for display."""
    if isinstance(resource, Issue):
        return "Issue"
    elif isinstance(resource, PullRequest):
        return "PR"
    elif isinstance(resource, Discussion):
        return "Discussion"
    return "Unknown"


def _get_source_url(resource: GitHubResource) -> str:
    """Get the source URL for the resource."""
    if isinstance(resource, Issue):
        return f"https://github.com/{_extract_owner_repo(resource)}/issues/{resource.number}"
    elif isinstance(resource, PullRequest):
        return f"https://github.com/{_extract_owner_repo(resource)}/pull/{resource.number}"
    elif isinstance(resource, Discussion):
        return f"https://github.com/{_extract_owner_repo(resource)}/discussions/{resource.number}"
    return "unknown"


def _extract_owner_repo(resource: GitHubResource) -> str:
    """Extract owner/repo from the author URL (simplified)."""
    # This is a placeholder - in a real implementation we'd store this
    # For now, we'll return a placeholder
    return "owner/repo"
