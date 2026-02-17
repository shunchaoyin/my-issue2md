# issue2md - 技术实现方案

> 版本: 1.0
> 创建日期: 2024-01-17
> 状态: 待评审

---

## 1. 技术上下文总结

### 1.1 技术选型

| 类别 | 技术选择 | 理由 |
|------|----------|------|
| **编程语言** | Python 3.10+ | 项目宪法要求，类型注解支持完善 |
| **HTTP 客户端** | requests | 简单、稳定、文档完善 |
| **GitHub API** | REST API v3 + GraphQL API v4 | Discussion 必须使用 GraphQL |
| **CLI 参数解析** | argparse (标准库) | 避免引入额外依赖 |
| **Markdown 处理** | 字符串拼接 | 避免引入第三方模板引擎 |
| **测试框架** | unittest (标准库) | 遵循宪法优先使用标准库 |

### 1.2 外部依赖

```
requests>=2.31.0
```

### 1.3 GitHub API 策略

| 资源类型 | API 类型 | 端点 |
|----------|----------|------|
| Issue | REST API | `GET /repos/{owner}/{repo}/issues/{number}` |
| Pull Request | REST API | `GET /repos/{owner}/{repo}/pulls/{number}` + `/comments` |
| Discussion | GraphQL API | 必须使用 GraphQL（REST API 支持不完整） |

**决策**: 为保持一致性，MVP 阶段统一使用 REST API（Issue/PR），Discussion 暂不实现或使用 GraphQL。

---

## 2. "合宪性"审查

### 2.1 第一条：简单性原则 (Simplicity First)

| 宪法条款 | 检查项 | 状态 |
|----------|--------|------|
| 1.1 YAGNI | 只实现 spec.md 明确要求的功能 | ✅ 无额外功能 |
| 1.2 标准库优先 | 使用 argparse, unittest, sys, os | ✅ 最小依赖 |
| 1.3 反过度工程 | 简单函数 + dataclass > 复杂类继承 | ✅ 无抽象基类 |

**审查结论**: 符合。数据模型使用 `@dataclass`，无复杂继承体系。

### 2.2 第二条：测试先行铁律 (Test-First Imperative)

| 宪法条款 | 检查项 | 状态 |
|----------|--------|------|
| 2.1 TDD 循环 | Red-Green-Refactor | ✅ 开发流程遵守 |
| 2.2 表格驱动 | pytest.mark.parametrize / unittest subTest | ✅ 测试用例组织 |
| 2.3 拒绝 Mocks | 优先集成测试，真实 API 调用 | ✅ MVP 阶段可接受少量网络测试 |

**审查结论**: 符合。测试优先编写，使用表格驱动风格。

### 2.3 第三条：明确性原则 (Clarity and Explicitness)

| 宪法条款 | 检查项 | 状态 |
|----------|--------|------|
| 3.1 错误处理 | 所有错误显式处理，使用 `raise ... from ...` | ✅ 见错误处理设计 |
| 3.2 无全局变量 | 依赖通过参数注入 | ✅ Config 对象传递 |

**审查结论**: 符合。无全局配置，所有依赖显式传递。

---

## 3. 项目结构细化

### 3.1 目录结构

```
issue2md/
├── cmd/
│   ├── issue2md/
│   │   └── __main__.py          # CLI 入口点
│   └── issue2mdweb/             # 未来 Web 版本（占位）
├── internal/
│   ├── __init__.py
│   ├── cli/                     # 命令行接口
│   │   ├── __init__.py
│   │   └── parser.py            # 参数解析
│   ├── config/                  # 配置管理
│   │   ├── __init__.py
│   │   └── models.py            # Config dataclass
│   ├── parser/                  # URL 解析
│   │   ├── __init__.py
│   │   └── url.py               # parse_github_url()
│   ├── github/                  # GitHub API 客户端
│   │   ├── __init__.py
│   │   ├── client.py            # GitHubClient 类
│   │   ├── models.py            # 数据模型 (Issue, PR, Comment)
│   │   └── errors.py            # 自定义异常
│   └── converter/               # Markdown 转换
│       ├── __init__.py
│       ├── formatter.py         # convert_to_markdown()
│       └── templates.py         # 渲染辅助函数
├── web/                         # 未来 Web 资源（占位）
├── tests/
│   ├── __init__.py
│   ├── test_cli.py
│   ├── test_parser.py
│   ├── test_github.py
│   └── test_converter.py
├── pyproject.toml               # 项目配置
└── README.md
```

### 3.2 包职责与依赖关系

```
┌─────────────────────────────────────────────────────────────┐
│                      cmd/issue2md/__main__.py                │
│                         (CLI Entry Point)                    │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      internal/cli/                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  parse_args  │  │     run      │  │  _handle_error│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───┬───────────────────┬───────────────────┬────────────────┘
    │                   │                   │
    ▼                   ▼                   ▼
┌─────────┐      ┌──────────┐      ┌──────────────┐
│ config  │      │  parser  │      │   github     │
└─────────┘      └──────────┘      └──────────────┘
                                          │
                                          ▼
                                   ┌──────────────┐
                                   │  converter   │
                                   └──────────────┘
```

**依赖规则**:
- `cmd/` 可依赖所有 `internal/` 包
- `internal/cli` 可依赖 `config`, `parser`, `github`, `converter`
- `internal/github` 独立，仅依赖 `requests`
- `internal/converter` 仅依赖 `internal/github.models`
- `internal/parser` 独立，无外部依赖

---

## 4. 核心数据结构

### 4.1 数据模型 (internal/github/models.py)

```python
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, Optional, List

# ============================================================================
# 基础类型
# ============================================================================

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
    """评论/回复"""
    id: int
    author: str
    author_url: str
    created_at: datetime
    updated_at: datetime
    body: str
    reactions: Reaction = field(default_factory=Reaction)

    # 嵌套回复（按时间正序）
    replies: List[Comment] = field(default_factory=list)

    # PR Review Comment 特有字段
    is_review_comment: bool = False
    review_file_path: Optional[str] = None
    review_line: Optional[int] = None

    # Discussion 特有字段
    is_answer: bool = False


# ============================================================================
# 资源类型
# ============================================================================

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


# 联合类型（Python 3.10+ 使用 | 语法）
GitHubResource = Issue | PullRequest | Discussion
```

### 4.2 配置模型 (internal/config/models.py)

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import os
import argparse


@dataclass(frozen=True)
class Config:
    """全局配置（不可变）"""

    # GitHub 认证
    github_token: Optional[str] = None

    # 功能开关
    enable_reactions: bool = False
    enable_user_links: bool = False

    # 输出设置
    output_file: Optional[str] = None  # None = stdout

    @classmethod
    def from_env(cls) -> Config:
        """从环境变量创建基础配置"""
        return cls(
            github_token=os.getenv("GITHUB_TOKEN"),
        )

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> Config:
        """从命令行参数创建配置"""
        base = cls.from_env()
        return cls(
            github_token=base.github_token,
            enable_reactions=args.enable_reactions,
            enable_user_links=args.enable_user_links,
            output_file=args.output_file,
        )
```

### 4.3 URL 解析结果 (internal/parser/url.py)

```python
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


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
```

---

## 5. 接口设计

### 5.1 internal/parser/url.py

```python
def parse_github_url(url: str) -> ParsedURL:
    """
    解析 GitHub URL 并识别资源类型

    Args:
        url: GitHub URL (Issue/PR/Discussion)

    Returns:
        ParsedURL: 解析后的 URL 信息

    Raises:
        InvalidURLError: URL 格式无效
        UnsupportedResourceTypeError: 不支持的资源类型

    Examples:
        >>> parse_github_url("https://github.com/owner/repo/issues/123")
        ParsedURL(resource_type=ResourceType.ISSUE, owner='owner', repo='repo', number=123, ...)
    """
    # 1. 使用 urllib.parse.urlparse 解析 URL
    # 2. 验证域名是 github.com
    # 3. 解析路径: /{owner}/{repo}/{type}/{number}
    # 4. 根据 type 识别资源类型
    # 5. 返回 ParsedURL
    pass
```

### 5.2 internal/github/client.py

```python
class GitHubClient:
    """GitHub API 客户端"""

    API_BASE_URL = "https://api.github.com"
    ACCEPT_HEADER = "application/vnd.github.v3+json"

    def __init__(self, token: Optional[str] = None) -> None:
        """
        初始化客户端

        Args:
            token: GitHub Personal Access Token（可选）
        """
        self._token = token
        self._session: Optional[requests.Session] = None

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
            GitHubAPIError: API 请求失败
            ResourceNotFoundError: 资源不存在 (404)
            AuthenticationError: 认证失败 (401)
            RateLimitError: API 限流 (403)
        """
        pass

    def fetch_pull_request(
        self,
        owner: str,
        repo: str,
        number: int,
        include_reactions: bool = False,
    ) -> PullRequest:
        """获取 Pull Request 数据（含 Review Comments）"""
        pass

    # Discussion 支持延后到 v1.1
    # def fetch_discussion(...) -> Discussion:
    #     pass

    def close(self) -> None:
        """关闭 HTTP 会话"""
        if self._session:
            self._session.close()

    def __enter__(self) -> GitHubClient:
        return self

    def __exit__(self, *args) -> None:
        self.close()
```

### 5.3 internal/converter/formatter.py

```python
def convert_to_markdown(
    resource: GitHubResource,
    config: Config,
    output: TextIO,
) -> None:
    """
    将 GitHub 资源转换为 Markdown 并写入输出

    Args:
        resource: GitHub 资源数据
        config: 配置对象
        output: 输出流（文件对象或 sys.stdout）

    Raises:
        IOError: 写入失败
    """
    # 1. 生成 YAML Frontmatter
    # 2. 生成正文
    # 3. 生成评论部分
    # 4. 写入 output
    pass


# ========================================================================
# 内部辅助函数（不对外暴露）
# ========================================================================

def _render_frontmatter(resource: GitHubResource) -> str:
    """生成 YAML Frontmatter"""
    pass

def _render_body(resource: GitHubResource, enable_user_links: bool) -> str:
    """生成正文（标题、描述等）"""
    pass

def _render_comments(
    comments: List[Comment],
    enable_user_links: bool,
    enable_reactions: bool,
    indent_level: int = 0,
) -> str:
    """
    生成评论部分（按时间正序）

    实现要点：
    - 递归处理嵌套回复（使用引用块 >）
    - PR Review Comment 添加文件路径标记
    - Discussion Answer 添加 ✅ 标记
    """
    pass

def _format_user_link(username: str, enabled: bool) -> str:
    """格式化用户为 @username 或 [@username](url)"""
    pass

def _format_datetime(dt: datetime) -> str:
    """格式化为 ISO 8601 UTC 字符串"""
    pass

def _format_reactions(reactions: Reaction) -> str:
    """格式化 Reactions 为 "👍 5, 👎 0, ...""""
    pass
```

### 5.4 internal/cli/

```python
def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    解析命令行参数

    Args:
        args: 参数列表，None 表示使用 sys.argv[1:]

    Returns:
        argparse.Namespace: 解析后的参数

    Raises:
        SystemExit: 参数无效时退出（退出码 2）
    """
    pass


def run(config: Config, url: str) -> int:
    """
    主执行函数

    Args:
        config: 配置对象
        url: GitHub URL

    Returns:
        int: 退出码（0 成功，1 失败）

    流程:
        1. parse_github_url(url)
        2. GitHubClient().fetch_*()
        3. convert_to_markdown()
        4. 错误处理并输出到 stderr
    """
    pass
```

---

## 6. 错误处理设计

### 6.1 异常层次结构

```python
# internal/github/errors.py

class Issue2MDError(Exception):
    """issue2md 基础异常"""
    pass


class InvalidURLError(Issue2MDError):
    """无效的 URL 格式"""
    pass


class UnsupportedResourceTypeError(Issue2MDError):
    """不支持的资源类型"""
    pass


class GitHubAPIError(Issue2MDError):
    """GitHub API 错误"""

    def __init__(self, message: str, status_code: int, response_text: str):
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(message)


class ResourceNotFoundError(GitHubAPIError):
    """资源不存在 (404)"""
    pass


class AuthenticationError(GitHubAPIError):
    """认证失败 (401)"""
    pass


class RateLimitError(GitHubAPIError):
    """API 限流 (403)"""
    pass
```

### 6.2 错误处理模式

```python
# 示例：在 CLI 层处理错误

def run(config: Config, url: str) -> int:
    try:
        parsed = parse_github_url(url)
        with GitHubClient(token=config.github_token) as client:
            resource = client.fetch_issue(
                owner=parsed.owner,
                repo=parsed.repo,
                number=parsed.number,
                include_reactions=config.enable_reactions,
            )
        with _open_output(config.output_file) as f:
            convert_to_markdown(resource, config, f)
        return 0

    except InvalidURLError as e:
        print(f"Error: Invalid URL format - {e}", file=sys.stderr)
        return 1
    except ResourceNotFoundError as e:
        print(f"Error: Resource not found - {e}", file=sys.stderr)
        return 1
    except AuthenticationError:
        print("Error: Private repository. Please set GITHUB_TOKEN", file=sys.stderr)
        return 1
    except RateLimitError as e:
        print(f"Error: GitHub API rate limit exceeded - {e}", file=sys.stderr)
        return 1
    except (IOError, OSError) as e:
        print(f"Error: Cannot write to file - {e}", file=sys.stderr)
        return 1
    except Issue2MDError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        # 捕获未预期的异常
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
```

---

## 7. 测试策略

### 7.1 测试目录结构

```
tests/
├── __init__.py
├── test_parser.py           # URL 解析（纯函数，无网络）
├── test_github.py           # GitHub API 客户端（集成测试）
├── test_converter.py        # Markdown 转换（纯函数，无网络）
└── test_cli.py              # CLI 端到端测试
```

### 7.2 表格驱动测试示例

```python
# tests/test_parser.py

import unittest
from internal.parser.url import parse_github_url, ResourceType, InvalidURLError


class TestParseGitHubURL(unittest.TestCase):
    """URL 解析测试（表格驱动）"""

    def test_valid_urls(self):
        """测试有效的 GitHub URL"""
        test_cases = [
            # (input, expected_type, expected_owner, expected_repo, expected_number)
            ("https://github.com/owner/repo/issues/123",
             ResourceType.ISSUE, "owner", "repo", 123),
            ("https://github.com/owner/repo/pull/456",
             ResourceType.PULL_REQUEST, "owner", "repo", 456),
            ("https://github.com/foo/bar/issues/1",
             ResourceType.ISSUE, "foo", "bar", 1),
        ]

        for url, exp_type, exp_owner, exp_repo, exp_num in test_cases:
            with self.subTest(url=url):
                result = parse_github_url(url)
                self.assertEqual(result.resource_type, exp_type)
                self.assertEqual(result.owner, exp_owner)
                self.assertEqual(result.repo, exp_repo)
                self.assertEqual(result.number, exp_num)

    def test_invalid_urls(self):
        """测试无效的 URL"""
        test_cases = [
            "https://example.com/not-github",
            "https://github.com/owner/repo/invalid/123",
            "not-a-url",
            "https://github.com/owner/repo/issues/abc",  # 非数字
        ]

        for url in test_cases:
            with self.subTest(url=url):
                with self.assertRaises(InvalidURLError):
                    parse_github_url(url)
```

### 7.3 集成测试策略

```python
# tests/test_github.py

import unittest
import os
from internal.github.client import GitHubClient, ResourceNotFoundError


@unittest.skipIf(not os.getenv("GITHUB_TOKEN"), "需要 GITHUB_TOKEN")
class TestGitHubClientIntegration(unittest.TestCase):
    """GitHub API 集成测试（需要网络和 Token）"""

    def setUp(self):
        self.client = GitHubClient(token=os.getenv("GITHUB_TOKEN"))

    def tearDown(self):
        self.client.close()

    def test_fetch_real_issue(self):
        """测试获取真实的 Issue"""
        # 使用一个公开的、稳定存在的 Issue
        issue = self.client.fetch_issue("python", "cpython", 12345)

        self.assertEqual(issue.number, 12345)
        self.assertIsInstance(issue.title, str)
        self.assertIsInstance(issue.author, str)
```

---

## 8. 实现里程碑

### Phase 1: 基础设施 (Day 1-2)
- [ ] 项目结构搭建
- [ ] 配置 `pyproject.toml`
- [ ] 实现 URL 解析器 (`internal/parser/url.py`)
- [ ] 编写 URL 解析测试

### Phase 2: GitHub API 客户端 (Day 3-4)
- [ ] 实现数据模型 (`internal/github/models.py`)
- [ ] 实现错误类 (`internal/github/errors.py`)
- [ ] 实现 Issue 获取 (`GitHubClient.fetch_issue`)
- [ ] 编写集成测试

### Phase 3: Markdown 转换 (Day 5-6)
- [ ] 实现 YAML Frontmatter 渲染
- [ ] 实现正文渲染
- [ ] 实现评论渲染（含嵌套）
- [ ] 编写单元测试

### Phase 4: CLI 集成 (Day 7)
- [ ] 实现参数解析 (`internal/cli/parser.py`)
- [ ] 实现主流程 (`internal/cli/run`)
- [ ] 实现 CLI 入口 (`cmd/issue2md/__main__.py`)
- [ ] 端到端测试

### Phase 5: PR 支持 (Day 8-9)
- [ ] 实现 PR 获取
- [ ] 实现 Review Comments 处理
- [ ] 测试

### Phase 6: 打包与文档 (Day 10)
- [ ] 完善 README
- [ ] 添加使用示例
- [ ] 准备 PyPI 发布

---

## 9. 开发工作流

```bash
# 1. 创建功能分支
git checkout -b feature/fetch-issue

# 2. 编写失败的测试（Red）
# vim tests/test_github.py

# 3. 运行测试确认失败
python -m unittest tests.test_github

# 4. 实现功能使测试通过（Green）
# vim internal/github/client.py

# 5. 重构优化（Refactor）

# 6. 提交
git add .
git commit -m "feat(github): implement Issue fetching"

# 7. 推送并创建 PR
git push origin feature/fetch-issue
```

---

## 10. 待确认事项

| 问题 | 影响 | 建议 |
|------|------|------|
| Discussion 支持 | 需要 GraphQL API | MVP 阶段延后 |
| 评论分页 | 大型 Issue 评论多 | MVP 限制前 100 条 |
| HTML 转 Markdown | GitHub API 返回 HTML | 使用 GitHub 的 Markdown API |
| 并发请求 | 性能优化 | MVP 阶段使用同步请求 |

---

## 附录 A: Git Commit 规范

遵循 Conventional Commits:

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(parser): add Discussion URL support` |
| `fix` | Bug 修复 | `fix(cli): handle missing output file` |
| `refactor` | 重构 | `refactor(converter): simplify reaction rendering` |
| `test` | 测试 | `test(github): add integration tests` |
| `docs` | 文档 | `docs(readme): update installation guide` |
| `chore` | 构建/工具 | `chore: update pyproject.toml` |
