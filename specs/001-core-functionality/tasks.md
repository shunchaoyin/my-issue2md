# issue2md - 开发任务列表

> 本文档将技术方案分解为原子化的、可被 AI 直接执行的任务列表。
>
> **约定:**
> - `[P]` = 可并行执行的任务（无依赖关系）
> - `T-` = 测试任务（Test）
> - `I-` = 实现任务（Implementation）
> - 任务按依赖关系排序，先测试后实现（TDD）

---

## Phase 1: Foundation (基础设施)

**目标**: 搭建项目结构，定义数据模型和配置

### 1.1 项目配置

- [ ] **T-001** [P] 编写 `pyproject.toml` 配置测试（验证依赖声明）
  - 文件: `tests/test_pyproject.py`
  - 内容: 验证 `requests` 依赖正确声明

- [ ] **I-001** 创建 `pyproject.toml` 项目配置文件
  - 文件: `pyproject.toml`
  - 内容: 项目元数据 + `requests>=2.31.0` 依赖
  - 依赖: T-001

- [ ] **I-002** [P] 创建所有 `__init__.py` 占位文件
  - 文件: `internal/__init__.py`, `internal/cli/__init__.py`, `internal/config/__init__.py`, `internal/parser/__init__.py`, `internal/github/__init__.py`, `internal/converter/__init__.py`, `tests/__init__.py`
  - 内容: 空文件或 `__all__ = []`

### 1.2 错误处理模型

- [ ] **T-002** 编写错误类测试（表格驱动）
  - 文件: `tests/test_errors.py`
  - 内容: 测试 `InvalidURLError`, `UnsupportedResourceTypeError`, `GitHubAPIError` 等异常类
  - 测试用例:
    - 验证异常继承关系
    - 验证 `GitHubAPIError` 存储状态码和响应文本

- [ ] **I-003** 实现错误类层次结构
  - 文件: `internal/github/errors.py`
  - 内容:
    - `Issue2MDError` 基类
    - `InvalidURLError`
    - `UnsupportedResourceTypeError`
    - `GitHubAPIError` (含 `status_code`, `response_text`)
    - `ResourceNotFoundError`
    - `AuthenticationError`
    - `RateLimitError`
  - 依赖: T-002

### 1.3 GitHub 数据模型

- [ ] **T-003** 编写 `Reaction` dataclass 测试
  - 文件: `tests/test_github_models.py`
  - 内容: 测试 `Reaction` 类的创建、默认值、不可变性
  - 测试用例:
    - 空构造函数验证默认值为 0
    - 部分字段赋值验证
    - `frozen=True` 验证不可修改

- [ ] **T-004** [P] 编写 `Comment` dataclass 测试
  - 文件: `tests/test_github_models.py` (追加)
  - 内容: 测试 `Comment` 类的字段、默认值、嵌套回复

- [ ] **T-005** [P] 编写 `Issue` dataclass 测试
  - 文件: `tests/test_github_models.py` (追加)
  - 内容: 测试 `Issue` 类的字段、status 枚举验证

- [ ] **T-006** [P] 编写 `PullRequest` dataclass 测试
  - 文件: `tests/test_github_models.py` (追加)
  - 内容: 测试 `PullRequest` 类的字段、status 枚举验证

- [ ] **T-007** [P] 编写 `Discussion` dataclass 测试
  - 文件: `tests/test_github_models.py` (追加)
  - 内容: 测试 `Discussion` 类的字段

- [ ] **I-004** 实现 GitHub 数据模型
  - 文件: `internal/github/models.py`
  - 内容:
    - `@dataclass(frozen=True) class Reaction`
    - `@dataclass(frozen=True) class Comment`
    - `@dataclass(frozen=True) class Issue`
    - `@dataclass(frozen=True) class PullRequest`
    - `@dataclass(frozen=True) class Discussion`
    - `GitHubResource` 类型别名
  - 依赖: T-003, T-004, T-005, T-006, T-007

### 1.4 配置模型

- [ ] **T-008** 编写 `Config` dataclass 测试
  - 文件: `tests/test_config.py`
  - 内容: 测试 `Config` 类的创建、`from_env()`, `from_args()` 方法
  - 测试用例:
    - 默认值验证
    - `from_env()` 读取 `GITHUB_TOKEN`
    - `from_args()` 合并环境变量和参数

- [ ] **I-005** 实现配置模型
  - 文件: `internal/config/models.py`
  - 内容:
    - `@dataclass(frozen=True) class Config`
    - `from_env()` 类方法
    - `from_args()` 类方法
  - 依赖: T-008

### 1.5 URL 解析模型

- [ ] **T-009** 编写 `ResourceType` 枚举测试
  - 文件: `tests/test_parser_models.py`
  - 内容: 测试 `ResourceType` 枚举值

- [ ] **T-010** 编写 `ParsedURL` dataclass 测试
  - 文件: `tests/test_parser_models.py` (追加)
  - 内容: 测试 `ParsedURL` 字段完整性

- [ ] **I-006** 实现解析结果模型
  - 文件: `internal/parser/url.py` (第一部分)
  - 内容:
    - `class ResourceType(Enum)`
    - `@dataclass(frozen=True) class ParsedURL`
  - 依赖: T-009, T-010

---

## Phase 2: GitHub Fetcher (API 交互)

**目标**: 实现 GitHub API 客户端，支持 Issue 和 PR 获取

### 2.1 URL 解析器

- [ ] **T-011** 编写 `parse_github_url()` 有效 URL 测试（表格驱动）
  - 文件: `tests/test_parser.py`
  - 内容: 测试各种有效的 GitHub URL
  - 测试用例:
    - Issue URLs: `https://github.com/owner/repo/issues/123`
    - PR URLs: `https://github.com/owner/repo/pull/456`
    - Discussion URLs: `https://github.com/owner/repo/discussions/78`
    - 不同 owner/repo 组合

- [ ] **T-012** 编写 `parse_github_url()` 无效 URL 测试（表格驱动）
  - 文件: `tests/test_parser.py` (追加)
  - 内容: 测试各种无效的 URL
  - 测试用例:
    - 非 github.com 域名
    - 路径格式错误
    - 类型不支持
    - number 非数字

- [ ] **I-007** 实现 `parse_github_url()` 函数
  - 文件: `internal/parser/url.py` (第二部分)
  - 内容: `def parse_github_url(url: str) -> ParsedURL`
  - 依赖: T-011, T-012, I-006
  - 实现:
    - 使用 `urllib.parse.urlparse` 解析
    - 验证域名是 `github.com`
    - 解析路径提取 `{owner}/{repo}/{type}/{number}`
    - 返回 `ParsedURL` 或抛出 `InvalidURLError`

### 2.2 GitHub 客户端 - Issue 获取

- [ ] **T-013** 编写 `GitHubClient.__init__()` 测试
  - 文件: `tests/test_github_client.py`
  - 内容: 测试客户端初始化、token 存储

- [ ] **T-014** [P] 编写 `GitHubClient._request()` 测试（使用 responses mock）
  - 文件: `tests/test_github_client.py` (追加)
  - 内容: 测试 HTTP 请求、认证头、错误状态码处理
  - 使用 `responses` 库 mock HTTP 响应

- [ ] **T-015** 编写 `fetch_issue()` 基本功能测试（mock 响应）
  - 文件: `tests/test_github_client.py` (追加)
  - 内容: 测试 Issue 数据解析
  - mock 响应: 包含基本 Issue 字段的 JSON

- [ ] **T-016** [P] 编写 `fetch_issue()` 带 Reactions 测试
  - 文件: `tests/test_github_client.py` (追加)
  - 内容: 测试 Reactions 数据解析

- [ ] **T-017** [P] 编写 `fetch_issue()` 评论解析测试
  - 文件: `tests/test_github_client.py` (追加)
  - 内容: 测试评论列表解析、嵌套回复

- [ ] **T-018** 编写 `fetch_issue()` 错误处理测试（表格驱动）
  - 文件: `tests/test_github_client.py` (追加)
  - 内容: 测试 404, 401, 403 等错误状态码
  - 测试用例:
    - 404 → `ResourceNotFoundError`
    - 401 → `AuthenticationError`
    - 403 rate limit → `RateLimitError`

- [ ] **I-008** 实现 `GitHubClient` 基本结构
  - 文件: `internal/github/client.py` (第一部分)
  - 内容:
    - `class GitHubClient` 定义
    - `__init__()` 方法
    - `close()` 方法
    - `__enter__()` / `__exit__()` 上下文管理器
  - 依赖: T-013

- [ ] **I-009** 实现 `_request()` 私有方法
  - 文件: `internal/github/client.py` (第二部分)
  - 内容: `def _request(method, url, **kwargs) -> dict`
  - 依赖: T-014, I-008
  - 实现:
    - 创建 `requests.Session`
    - 设置认证头（如有 token）
    - 发送请求
    - 处理错误状态码，抛出对应异常

- [ ] **I-010** 实现 `fetch_issue()` 方法
  - 文件: `internal/github/client.py` (第三部分)
  - 内容: `def fetch_issue(owner, repo, number, include_reactions) -> Issue`
  - 依赖: T-015, T-016, T-017, T-018, I-009
  - 实现:
    - 调用 `GET /repos/{owner}/{repo}/issues/{number}`
    - 解析响应 JSON 为 `Issue` 对象
    - 获取评论（如有）
    - 获取 reactions（如有）

- [ ] **T-019** [P] 编写 `fetch_issue()` 集成测试（真实 API）
  - 文件: `tests/test_github_integration.py`
  - 内容: 测试获取真实的 GitHub Issue
  - 标记: `@unittest.skipIf(not os.getenv("GITHUB_TOKEN"))`

### 2.3 GitHub 客户端 - PR 获取

- [ ] **T-020** 编写 `fetch_pull_request()` 基本功能测试（mock 响应）
  - 文件: `tests/test_github_client.py` (追加)
  - 内容: 测试 PR 数据解析、merged 状态处理

- [ ] **T-021** [P] 编写 `fetch_pull_request()` Review Comments 测试
  - 文件: `tests/test_github_client.py` (追加)
  - 内容: 测试 Review Comments 解析、文件路径和行号

- [ ] **T-022** [P] 编写 `fetch_pull_request()` 错误处理测试
  - 文件: `tests/test_github_client.py` (追加)
  - 内容: 测试 PR 特定错误场景

- [ ] **I-011** 实现 `fetch_pull_request()` 方法
  - 文件: `internal/github/client.py` (第四部分)
  - 内容: `def fetch_pull_request(owner, repo, number, include_reactions) -> PullRequest`
  - 依赖: T-020, T-021, T-022, I-009
  - 实现:
    - 调用 `GET /repos/{owner}/{repo}/pulls/{number}`
    - 调用 `GET /repos/{owner}/{repo}/pulls/{number}/comments`
    - 合并普通评论和 Review Comments（按时间排序）
    - 标记 Review Comment 的文件路径和行号

- [ ] **T-023** [P] 编写 `fetch_pull_request()` 集成测试（真实 API）
  - 文件: `tests/test_github_integration.py` (追加)
  - 内容: 测试获取真实的 GitHub PR

---

## Phase 3: Markdown Converter (转换逻辑)

**目标**: 实现将 GitHub 资源转换为 Markdown 格式

### 3.1 辅助格式化函数

- [ ] **T-024** 编写 `_format_user_link()` 测试（表格驱动）
  - 文件: `tests/test_converter.py`
  - 内容: 测试用户名格式化
  - 测试用例:
    - `enabled=False` → `@username`
    - `enabled=True` → `[@username](https://github.com/username)`

- [ ] **T-025** [P] 编写 `_format_datetime()` 测试（表格驱动）
  - 文件: `tests/test_converter.py` (追加)
  - 内容: 测试 datetime 转 ISO 8601 UTC 字符串

- [ ] **T-026** [P] 编写 `_format_reactions()` 测试（表格驱动）
  - 文件: `tests/test_converter.py` (追加)
  - 内容: 测试 Reactions 格式化
  - 测试用例:
    - 空 reactions → 空字符串
    - 部分非零 → "👍 5, ❤️ 3"
    - 全部非零 → 完整字符串

- [ ] **I-012** 实现辅助格式化函数
  - 文件: `internal/converter/formatter.py` (第一部分)
  - 内容:
    - `def _format_user_link(username, enabled) -> str`
    - `def _format_datetime(dt) -> str`
    - `def _format_reactions(reactions) -> str`
  - 依赖: T-024, T-025, T-026

### 3.2 YAML Frontmatter 渲染

- [ ] **T-027** 编写 `_render_frontmatter()` Issue 测试
  - 文件: `tests/test_converter.py` (追加)
  - 内容: 测试 Issue 的 YAML Frontmatter 生成
  - 验证:
    - 以 `---` 开头和结尾
    - 包含所有必需字段
    - Reactions 格式正确（如有）

- [ ] **T-028** [P] 编写 `_render_frontmatter()` PR 测试
  - 文件: `tests/test_converter.py` (追加)
  - 内容: 测试 PR 的 YAML Frontmatter（无 reactions）

- [ ] **T-029** [P] 编写 `_render_frontmatter()` Discussion 测试
  - 文件: `tests/test_converter.py` (追加)
  - 内容: 测试 Discussion 的 YAML Frontmatter

- [ ] **I-013** 实现 `_render_frontmatter()` 函数
  - 文件: `internal/converter/formatter.py` (第二部分)
  - 内容: `def _render_frontmatter(resource) -> str`
  - 依赖: T-027, T-028, T-029, I-012
  - 实现:
    - 根据 resource 类型提取字段
    - 生成 YAML 格式

### 3.3 正文渲染

- [ ] **T-030** 编写 `_render_body()` Issue 测试
  - 文件: `tests/test_converter.py` (追加)
  - 内容: 测试 Issue 正文渲染
  - 验证:
    - 标题格式 `# [Issue #123] 标题`
    - 作者、时间、状态行
    - 标签列表
    - body 内容保留

- [ ] **T-031** [P] 编写 `_render_body()` PR 测试
  - 文件: `tests/test_converter.py` (追加)
  - 内容: 测试 PR 正文渲染（merged 状态）

- [ ] **I-014** 实现 `_render_body()` 函数
  - 文件: `internal/converter/formatter.py` (第三部分)
  - 内容: `def _render_body(resource, enable_user_links) -> str`
  - 依赖: T-030, T-031, I-012, I-013

### 3.4 评论渲染

- [ ] **T-032** 编写 `_render_comments()` 基本测试
  - 文件: `tests/test_converter.py` (追加)
  - 内容: 测试单层评论渲染
  - 验证:
    - 评论标题格式 `### @username (timestamp)`
    - 评论内容
    - Reactions（如有）

- [ ] **T-033** [P] 编写 `_render_comments()` 嵌套测试
  - 文件: `tests/test_converter.py` (追加)
  - 内容: 测试嵌套回复渲染
  - 验证:
    - 使用 `>` 引用块
    - 多层嵌套缩进

- [ ] **T-034** [P] 编写 `_render_comments()` PR Review Comment 测试
  - 文件: `tests/test_converter.py` (追加)
  - 内容: 测试 PR Review Comment 渲染
  - 验证:
    - `[Review Comment]` 标记
    - `**File:** \`path:line\`` 格式

- [ ] **T-035** [P] 编写 `_render_comments()` Discussion Answer 测试
  - 文件: `tests/test_converter.py` (追加)
  - 内容: 测试 Discussion Answer 渲染
  - 验证: `✅ [Accepted Answer]` 标记

- [ ] **I-015** 实现 `_render_comments()` 函数
  - 文件: `internal/converter/formatter.py` (第四部分)
  - 内容: `def _render_comments(comments, enable_user_links, enable_reactions, indent_level=0) -> str`
  - 依赖: T-032, T-033, T-034, T-035, I-012
  - 实现:
    - 递归处理嵌套回复
    - PR Review Comment 特殊标记
    - Discussion Answer 特殊标记
    - Reactions 渲染

### 3.5 主转换函数

- [ ] **T-036** 编写 `convert_to_markdown()` Issue 测试
  - 文件: `tests/test_converter.py` (追加)
  - 内容: 测试完整 Issue 转换
  - 使用 `io.StringIO` 验证输出

- [ ] **T-037** [P] 编写 `convert_to_markdown()` PR 测试
  - 文件: `tests/test_converter.py` (追加)
  - 内容: 测试完整 PR 转换

- [ ] **T-038** [P] 编写 `convert_to_markdown()` 文件输出测试
  - 文件: `tests/test_converter.py` (追加)
  - 内容: 测试写入文件（使用临时文件）

- [ ] **I-016** 实现 `convert_to_markdown()` 主函数
  - 文件: `internal/converter/formatter.py` (第五部分)
  - 内容: `def convert_to_markdown(resource, config, output) -> None`
  - 依赖: T-036, T-037, T-038, I-014, I-015, I-005
  - 实现:
    - 调用 `_render_frontmatter()`
    - 调用 `_render_body()`
    - 调用 `_render_comments()`
    - 合并并写入 output

---

## Phase 4: CLI Assembly (命令行集成)

**目标**: 实现命令行接口，组装所有模块

### 4.1 CLI 参数解析

- [ ] **T-039** 编写 `parse_args()` 基本测试（表格驱动）
  - 文件: `tests/test_cli.py`
  - 内容: 测试参数解析
  - 测试用例:
    - 只有 URL
    - URL + 输出文件
    - URL + flags
    - 所有参数组合

- [ ] **T-040** [P] 编写 `parse_args()` 错误处理测试
  - 文件: `tests/test_cli.py` (追加)
  - 内容: 测试无效参数（argparse 自动处理）

- [ ] **I-017** 实现 `parse_args()` 函数
  - 文件: `internal/cli/parser.py`
  - 内容: `def parse_args(args=None) -> argparse.Namespace`
  - 依赖: T-039, T-040
  - 实现:
    - 创建 `ArgumentParser`
    - 添加 `url` 位置参数
    - 添加 `output_file` 可选位置参数
    - 添加 `-enable-reactions` flag
    - 添加 `-enable-user-links` flag

### 4.2 主执行流程

- [ ] **T-041** 编写 `run()` 成功路径测试
  - 文件: `tests/test_cli.py` (追加)
  - 内容: 测试完整成功流程（mock 所有依赖）
  - 验证: 返回 0

- [ ] **T-042** [P] 编写 `run()` 错误处理测试（表格驱动）
  - 文件: `tests/test_cli.py` (追加)
  - 内容: 测试各种错误场景
  - 测试用例:
    - `InvalidURLError` → stderr 错误，返回 1
    - `ResourceNotFoundError` → stderr 错误，返回 1
    - `AuthenticationError` → stderr 错误，返回 1
    - `RateLimitError` → stderr 错误，返回 1
    - `IOError` → stderr 错误，返回 1

- [ ] **T-043** [P] 编写 `run()` 输出重定向测试
  - 文件: `tests/test_cli.py` (追加)
  - 内容: 测试输出到文件 vs stdout

- [ ] **I-018** 实现 `run()` 主函数
  - 文件: `internal/cli/run.py`
  - 内容: `def run(config, url) -> int`
  - 依赖: T-041, T-042, T-043, I-001, I-005, I-007, I-010, I-011, I-016
  - 实现:
    - 解析 URL
    - 获取资源
    - 转换为 Markdown
    - 写入输出
    - 错误处理

### 4.3 CLI 入口点

- [ ] **T-044** 编写 `__main__.py` 端到端测试
  - 文件: `tests/test_cli_e2e.py`
  - 内容: 测试完整 CLI 执行（使用 subprocess）
  - 使用 mock GitHub 数据

- [ ] **I-019** 实现 CLI 入口点
  - 文件: `cmd/issue2md/__main__.py`
  - 内容: `main()` 函数
  - 依赖: T-044, I-017, I-018, I-005
  - 实现:
    - 调用 `parse_args()`
    - 创建 `Config`
    - 调用 `run()`
    - 返回退出码

### 4.4 打包配置

- [ ] **I-020** 配置 CLI 入口点
  - 文件: `pyproject.toml` (更新)
  - 内容: 添加 `[project.scripts]` 配置
  - 依赖: I-001, I-019

---

## 附加任务

### 文档

- [ ] **I-021** 编写 `README.md`
  - 文件: `README.md`
  - 内容: 项目介绍、安装、使用示例

### 版本控制

- [ ] **I-022** 初始化 Git 仓库并提交
  - 命令: `git init`, `git add .`, `git commit`

---

## 任务统计

| Phase | 测试任务 | 实现任务 | 总计 |
|-------|---------|---------|------|
| Phase 1: Foundation | 9 | 6 | 15 |
| Phase 2: GitHub Fetcher | 13 | 5 | 18 |
| Phase 3: Converter | 15 | 5 | 20 |
| Phase 4: CLI Assembly | 6 | 4 | 10 |
| 附加 | 0 | 3 | 3 |
| **总计** | **43** | **23** | **66** |

---

## 依赖关系摘要

```
Phase 1: Foundation (无外部依赖)
  ↓
Phase 2: GitHub Fetcher (依赖 Phase 1 的数据模型和错误类)
  ↓
Phase 3: Converter (依赖 Phase 1 的数据模型 + Phase 2 的 API 客户端)
  ↓
Phase 4: CLI Assembly (依赖所有前置阶段)
```

---

## 执行建议

1. **严格遵循 TDD**: 每个实现任务 (I-xxx) 必须在对应的测试任务 (T-xxx) 完成后执行
2. **并行执行**: 标记 `[P]` 的任务可以并行开发，提高效率
3. **小步提交**: 每完成一个任务就提交一次，保持原子性
4. **测试驱动**: 运行测试确保失败后再实现，实现后确保通过
