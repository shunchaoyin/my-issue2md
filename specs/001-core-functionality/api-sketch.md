# issue2md - API 接口草图

> 本文档描述 `internal/` 包对外暴露的主要接口，作为后续 TDD 开发的参考。

## 设计原则

1. **遵循项目宪法**：简单性优先，避免过度抽象
2. **显式依赖**：所有依赖通过函数参数注入，不使用全局变量
3. **错误处理**：使用 `raise ... from ...` 传递错误
4. **类型明确**：使用 `dataclass` 定义清晰的数据结构

---

## 1. internal/config - 配置管理

```python
# internal/config/__init__.py

from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Config:
    """全局配置"""

    # GitHub 认证 Token（从环境变量读取）
    github_token: Optional[str] = None

    # 功能开关
    enable_reactions: bool = False
    enable_user_links: bool = False

    # 输出设置
    output_file: Optional[str] = None  # None 表示输出到 stdout

    @classmethod
    def from_env(cls) -> "Config":
        """从环境变量创建配置"""
        import os
        return cls(
            github_token=os.getenv("GITHUB_TOKEN"),
        )

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> "Config":
        """从命令行参数创建配置"""
        base = cls.from_env()
        return cls(
            github_token=base.github_token,
            enable_reactions=args.enable_reactions,
            enable_user_links=args.enable_user_links,
            output_file=args.output_file,
        )
```

---

## 2. internal/parser - URL 解析

```python
# internal/parser/__init__.py

from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlparse

class ResourceType(Enum):
    """GitHub 资源类型"""
    ISSUE = "issue"
    PULL_REQUEST = "pull_request"
    DISCUSSION = "discussion"

@dataclass(frozen=True)
class ParsedURL:
    """解析后的 GitHub URL"""
    resource_type: ResourceType
    owner: str
    repo: str
    number: int
    original_url: str

def parse_github_url(url: str) -> ParsedURL:
    """
    解析 GitHub URL 并识别资源类型

    Args:
        url: GitHub URL (Issue/PR/Discussion)

    Returns:
        ParsedURL: 解析后的 URL 信息

    Raises:
        ValueError: 无效的 URL 格式
        NotImplementedError: 不支持的 URL 类型

    Examples:
        >>> parse_github_url("https://github.com/owner/repo/issues/123")
        ParsedURL(resource_type=ResourceType.ISSUE, owner='owner', repo='repo', number=123, ...)
    """
    # 实现细节：
    # 1. 验证域名是 github.com
    # 2. 解析路径：/{owner}/{repo}/{type}/{number}
    # 3. 根据 type 识别资源类型
    # 4. 返回 ParsedURL 对象
    pass
```

---

## 3. internal/github - GitHub API 客户端

```python
# internal/github/__init__.py

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Literal

@dataclass(frozen=True)
class Reaction:
    """Reaction 统计"""
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
    """评论"""
    id: int
    author: str
    author_url: str
    created_at: datetime
    updated_at: datetime
    body: str
    reactions: Reaction = field(default_factory=Reaction)

    # 嵌套回复
    replies: List["Comment"] = field(default_factory=list)

    # PR Review Comment 特有字段
    is_review_comment: bool = False
    review_file_path: Optional[str] = None
    review_line: Optional[int] = None

    # Discussion 特有字段
    is_answer: bool = False

@dataclass(frozen=True)
class Issue:
    """Issue 数据"""
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
    """Pull Request 数据"""
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
    """Discussion 数据"""
    number: int
    title: str
    author: str
    author_url: str
    created_at: datetime
    updated_at: datetime
    status: Literal["open", "closed"]
    body: str
    comments: List[Comment] = field(default_factory=list)

# 联合类型
GitHubResource = Issue | PullRequest | Discussion

class GitHubClient:
    """GitHub API 客户端"""

    def __init__(self, token: Optional[str] = None):
        """
        初始化客户端

        Args:
            token: GitHub Personal Access Token（可选）
        """
        self._token = token
        self._session = None  # 延迟创建 requests.Session

    def fetch_issue(
        self,
        owner: str,
        repo: str,
        number: int,
        include_reactions: bool = False,
    ) -> Issue:
        """
        获取 Issue 数据

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            number: Issue 编号
            include_reactions: 是否包含 Reactions

        Returns:
            Issue: Issue 数据

        Raises:
            HTTPError: API 请求失败
            ValueError: 数据解析失败
        """
        pass

    def fetch_pull_request(
        self,
        owner: str,
        repo: str,
        number: int,
        include_reactions: bool = False,
    ) -> PullRequest:
        """
        获取 Pull Request 数据

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            number: PR 编号
            include_reactions: 是否包含 Reactions

        Returns:
            PullRequest: PR 数据（包含 Review Comments）

        Raises:
            HTTPError: API 请求失败
            ValueError: 数据解析失败
        """
        pass

    def fetch_discussion(
        self,
        owner: str,
        repo: str,
        number: int,
        include_reactions: bool = False,
    ) -> Discussion:
        """
        获取 Discussion 数据

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            number: Discussion 编号
            include_reactions: 是否包含 Reactions

        Returns:
            Discussion: Discussion 数据

        Raises:
            HTTPError: API 请求失败
            ValueError: 数据解析失败
        """
        pass

    def _request(self, method: str, url: str, **kwargs) -> dict:
        """
        发送 HTTP 请求

        Args:
            method: HTTP 方法
            url: 请求 URL
            **kwargs: 传递给 requests 的参数

        Returns:
            dict: 解析后的 JSON 响应

        Raises:
            HTTPError: 请求失败，包含状态码和错误信息
        """
        pass

    def close(self):
        """关闭会话"""
        if self._session:
            self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
```

---

## 4. internal/converter - Markdown 转换

```python
# internal/converter/__init__.py

from typing import TextIO
from internal.github import GitHubResource, Issue, PullRequest, Discussion

def convert_to_markdown(
    resource: GitHubResource,
    config: "Config",
    output: TextIO,
) -> None:
    """
    将 GitHub 资源转换为 Markdown 并写入输出

    Args:
        resource: GitHub 资源数据（Issue/PR/Discussion）
        config: 配置对象
        output: 输出流（文件对象或 sys.stdout）

    Raises:
        IOError: 写入失败
    """
    # 实现细节：
    # 1. 调用 _render_frontmatter() 生成 YAML Frontmatter
    # 2. 调用 _render_body() 生成正文
    # 3. 调用 _render_comments() 生成评论部分
    # 4. 写入 output
    pass

def _render_frontmatter(resource: GitHubResource) -> str:
    """生成 YAML Frontmatter"""
    pass

def _render_body(resource: GitHubResource, enable_user_links: bool) -> str:
    """生成正文（标题、描述等）"""
    pass

def _render_comments(
    comments: list,
    enable_user_links: bool,
    enable_reactions: bool,
) -> str:
    """
    生成评论部分（按时间正序）

    实现要点：
    - 递归处理嵌套回复（使用引用块）
    - PR Review Comment 添加文件路径标记
    - Discussion Answer 添加 ✅ 标记
    """
    pass

def _format_user_link(username: str, enabled: bool) -> str:
    """
    格式化用户链接

    Args:
        username: GitHub 用户名
        enabled: 是否启用链接

    Returns:
        str: @username 或 [@username](url)
    """
    if enabled:
        return f"[@{username}](https://github.com/{username})"
    return f"@{username}"

def _format_datetime(dt: datetime) -> str:
    """
    格式化日期时间为 ISO 8601 UTC 字符串

    Args:
        dt: datetime 对象

    Returns:
        str: ISO 8601 格式字符串
    """
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def _format_reactions(reactions: Reaction) -> str:
    """
    格式化 Reactions 为单行字符串

    Args:
        reactions: Reaction 对象

    Returns:
        str: "👍 5, 👎 0, 😄 2, ..."
    """
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
```

---

## 5. internal/cli - 命令行接口

```python
# internal/cli/__init__.py

import argparse
import sys
from typing import Optional
from internal.config import Config

def parse_args(args: Optional[list[str]] = None) -> argparse.Namespace:
    """
    解析命令行参数

    Args:
        args: 参数列表，None 表示使用 sys.argv[1:]

    Returns:
        argparse.Namespace: 解析后的参数

    Raises:
        SystemExit: 参数无效时退出（退出码 2）
    """
    parser = argparse.ArgumentParser(
        prog="issue2md",
        description="Convert GitHub Issues/PRs/Discussions to Markdown",
    )

    # 位置参数
    parser.add_argument(
        "url",
        help="GitHub Issue/PR/Discussion URL",
    )

    # 可选位置参数（输出文件）
    parser.add_argument(
        "output_file",
        nargs="?",
        default=None,
        help="Output file path (default: stdout)",
    )

    # Flags
    parser.add_argument(
        "-enable-reactions",
        action="store_true",
        help="Include reaction statistics",
    )

    parser.add_argument(
        "-enable-user-links",
        action="store_true",
        help="Render usernames as links to GitHub profiles",
    )

    return parser.parse_args(args)

def run(config: Config, url: str) -> int:
    """
    主执行函数

    Args:
        config: 配置对象
        url: GitHub URL

    Returns:
        int: 退出码（0 成功，1 失败）
    """
    # 实现细节：
    # 1. 解析 URL
    # 2. 获取资源数据
    # 3. 转换为 Markdown
    # 4. 写入输出
    # 5. 错误处理
    pass
```

---

## 6. 调用流程示例

```python
# cmd/issue2md/__main__.py

import sys
from internal.cli import run
from internal.config import Config

def main() -> int:
    # 1. 解析命令行参数
    args = parse_args()

    # 2. 创建配置
    config = Config.from_args(args)

    # 3. 执行主逻辑
    return run(config, args.url)

if __name__ == "__main__":
    sys.exit(main())
```

---

## 7. 测试策略

### 7.1 单元测试（表格驱动）

```python
# tests/test_parser.py

import pytest
from internal.parser import parse_github_url, ResourceType

@pytest.mark.parametrize(
    "url,expected_type,expected_owner,expected_repo,expected_number",
    [
        # 有效 URL
        (
            "https://github.com/owner/repo/issues/123",
            ResourceType.ISSUE,
            "owner",
            "repo",
            123,
        ),
        (
            "https://github.com/owner/repo/pull/456",
            ResourceType.PULL_REQUEST,
            "owner",
            "repo",
            456,
        ),
        (
            "https://github.com/owner/repo/discussions/78",
            ResourceType.DISCUSSION,
            "owner",
            "repo",
            78,
        ),
        # 无效 URL
        pytest.param(
            "https://example.com/not-github",
            None,
            None,
            None,
            None,
            marks=pytest.mark.raises(ValueError),
        ),
        # ... 更多测试用例
    ],
)
def test_parse_github_url(url, expected_type, expected_owner, expected_repo, expected_number):
    result = parse_github_url(url)
    assert result.resource_type == expected_type
    assert result.owner == expected_owner
    assert result.repo == expected_repo
    assert result.number == expected_number
```

### 7.2 集成测试

```python
# tests/test_integration.py

import os
from internal.cli import run
from internal.config import Config

def test_real_issue():
    """测试真实的 GitHub Issue（需要网络）"""
    config = Config(
        github_token=os.getenv("GITHUB_TOKEN"),
        enable_reactions=True,
        enable_user_links=True,
        output_file=None,  # stdout
    )
    url = "https://github.com/owner/repo/issues/123"
    exit_code = run(config, url)
    assert exit_code == 0
```

---

## 8. 依赖关系图

```
cmd/issue2md/__main__.py
    └── internal/cli.run()
        ├── internal/config.Config
        ├── internal/parser.parse_github_url()
        ├── internal/github.GitHubClient
        │   └── requests (外部依赖)
        └── internal/converter.convert_to_markdown()
            ├── GitHubResource (数据模型)
            └── sys.stdout / file
```

---

## 9. 待确认事项

1. **GitHub API 端点**：
   - Issue: `GET /repos/{owner}/{repo}/issues/{issue_number}`
   - PR: `GET /repos/{owner}/{repo}/pulls/{pull_number}`
   - PR Review Comments: `GET /repos/{owner}/{repo}/pulls/{pull_number}/comments`
   - Discussion: GraphQL API（REST API 不完整支持）

2. **Pagination**：
   - 是否支持评论超过 30 条的 Pagination？
   - MVP 阶段可限制获取前 100 条评论

3. **GraphQL vs REST**：
   - Discussion 需要使用 GraphQL API
   - Issue/PR 可以使用 REST API
   - 建议：统一使用 GraphQL（减少依赖复杂度）

4. **并发请求**：
   - 评论 + reactions 可能需要多次请求
   - MVP 阶段使用同步请求，保持简单
