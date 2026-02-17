# issue2md - 核心功能规格说明书

## 1. 用户故事

### 1.1 当前范围：CLI 工具

**作为一名开发者**，我经常需要归档或引用 GitHub 上的 Issue、Pull Request 和 Discussion，以便于：
- 本地文档归档
- 离线阅读和参考
- 在其他文档中引用
- 项目知识库沉淀

**我希望**能够通过一个简单的命令行工具，输入 GitHub URL，就能自动获取并转换为格式化的 Markdown 文件，而无需手动复制粘贴。

### 1.2 未来范围：Web 界面（Out of Scope）

**作为一名用户**，我希望：
- 通过 Web 界面输入 URL，直接在浏览器中预览和下载 Markdown
- 支持批量转换多个 URLs
- 提供 REST API 供其他服务集成
- 支持自定义 Markdown 模板

---

## 2. 功能性需求

### 2.1 URL 自动识别

工具必须能够自动识别并处理以下 GitHub URL 格式：

| 类型 | URL 格式 | 示例 |
|------|----------|------|
| Issue | `https://github.com/{owner}/{repo}/issues/{number}` | `https://github.com/owner/repo/issues/123` |
| Pull Request | `https://github.com/{owner}/{repo}/pull/{number}` | `https://github.com/owner/repo/pull/456` |
| Discussion | `https://github.com/{owner}/{repo}/discussions/{number}` | `https://github.com/owner/repo/discussions/78` |

**要求：**
- 解析 URL 结构自动判断类型
- 不需要用户手动指定类型参数
- 无效 URL 格式应返回清晰的错误信息

### 2.2 命令行接口

```bash
issue2md [flags] <url> [output_file]
```

**参数：**
- `url` (必需): GitHub Issue/PR/Discussion 的 URL
- `output_file` (可选): 输出文件路径，默认为 stdout

**Flags:**
- `-enable-reactions`: 包含 Reactions 统计信息（👍 👎 😄 等）
- `-enable-user-links`: 将用户名渲染为指向其 GitHub 主页的链接

**认证：**
- Token 仅通过环境变量 `GITHUB_TOKEN` 获取
- 不提供 `--token` 参数，防止在 Shell 历史中泄露密钥
- 公有仓库可无需认证访问

**使用示例：**
```bash
# 输出到 stdout
issue2md https://github.com/owner/repo/issues/123

# 输出到文件
issue2md https://github.com/owner/repo/issues/123 issue-123.md

# 启用 Reactions 和用户链接
issue2md -enable-reactions -enable-user-links https://github.com/owner/repo/pull/456 pr.md

# Discussion 转换
issue2md https://github.com/owner/repo/discussions/78 -o discussion.md
```

### 2.3 Markdown 输出格式

#### 2.3.1 YAML Frontmatter（必须）

```yaml
---
title: "[Issue/PR/Discussion] 标题"
url: "https://github.com/owner/repo/issues/123"
type: "issue"  # issue | pull_request | discussion
number: 123
author: "username"
author_url: "https://github.com/username"
created_at: "2024-01-15T10:30:00Z"
updated_at: "2024-01-16T14:20:00Z"
status: "open"  # open | closed | merged
labels: ["bug", "enhancement"]  # 仅 Issue/PR
reactions:  # 启用 -enable-reactions 时
  thumbs_up: 5
  thumbs_down: 0
  laugh: 2
  hooray: 1
  confused: 0
  heart: 3
  rocket: 0
  eyes: 1
---
```

#### 2.3.2 正文结构

```markdown
# [Issue #123] 标题

**作者:** @username | **创建时间:** 2024-01-15 10:30:00 UTC | **状态:** Open

**标签:** bug, enhancement

---

## 描述

这里是 Issue 的正文内容...

### 代码示例

```python
def example():
    pass
```

## 评论 (按时间正序)

### @username (2024-01-15 14:20:00 UTC)

这是第一条评论...

> ### @other-user (2024-01-15 15:30:00 UTC)
>
> 这是嵌套回复...

### @reviewer (2024-01-16 09:00:00 UTC) [Review Comment]

**File:** `src/main.py:123`

这是 PR Review 评论内容...

### @author (2024-01-16 10:00:00 UTC) ✅ [Accepted Answer]

这是被标记为 Answer 的 Discussion 回复...

---

**生成于:** issue2md v1.0.0 | **来源:** https://github.com/owner/repo/issues/123
```

### 2.4 内容处理规则

| 场景 | 处理方式 |
|------|----------|
| 评论排序 | 统一按时间正序（最早在前） |
| PR Review Comments | 与普通评论平铺，添加 `[Review Comment]` 标记和文件路径信息 |
| 嵌套回复 | 使用 Markdown 引用块（`>`）体现层级关系 |
| Discussion Answer | 添加 ✅ `[Accepted Answer]` 标记 |
| 代码块 | 保留原始语言标记（如 \`\`\`python） |
| 图片 | 保留原始 GitHub 链接，不下载 |
| Reactions | 启用 `-enable-reactions` 时在每个评论下方显示统计 |
| 用户链接 | 启用 `-enable-user-links` 时 `@username` 渲染为 `[@username](https://github.com/username)` |

### 2.5 错误处理

| 错误场景 | 行为 |
|----------|------|
| 无效 URL 格式 | stderr 输出错误，退出码 1 |
| 资源不存在 (404) | stderr 输出 "Error: Resource not found"，退出码 1 |
| 私有仓库未认证 | stderr 输出 "Error: Private repository. Please set GITHUB_TOKEN"，退出码 1 |
| API 限流 (403) | stderr 透传 GitHub API 错误信息，退出码 1 |
| 网络错误 | stderr 输出错误详情，退出码 1 |
| 无写入权限 | stderr 输出 "Error: Cannot write to file"，退出码 1 |

**不实现复杂的重试机制**，保持 CLI 轻量。

---

## 3. 非功能性需求

### 3.1 架构设计原则

遵循项目宪法（constitution.md）：

1. **简单性优先**
   - 优先使用 Python 标准库
   - 避免不必要的抽象
   - 简单函数优于复杂类

2. **测试先行**
   - 所有功能从失败测试开始
   - 优先使用表格驱动测试
   - 避免过度 Mock

3. **明确性原则**
   - 所有错误显式处理
   - 使用 `raise ... from ...` 传递错误
   - 无全局变量传递状态

### 3.2 模块解耦

```
issue2md/
├── __main__.py           # CLI 入口
├── internal/
│   ├── cli.py            # 参数解析
│   ├── github_api.py     # GitHub API 客户端
│   ├── url_parser.py     # URL 解析和类型识别
│   ├── formatter.py      # Markdown 格式化
│   └── models.py         # 数据模型
└── tests/
    ├── test_cli.py
    ├── test_url_parser.py
    ├── test_github_api.py
    └── test_formatter.py
```

### 3.3 依赖管理

**必需依赖：**
- Python >= 3.10
- requests (HTTP 客户端)

**禁止引入：**
- 复杂的 CLI 框架（使用 argparse）
- 不必要的异步/并发库
- 重型模板引擎

---

## 4. 验收标准

### 4.1 功能测试用例

| ID | 测试场景 | 输入 | 预期输出 |
|----|----------|------|----------|
| T1 | 有效 Issue URL | `issue2md https://github.com/.../issues/123` | 输出完整 Markdown，type=issue |
| T2 | 有效 PR URL | `issue2md https://github.com/.../pull/456` | 输出完整 Markdown，type=pull_request，包含 Review Comments |
| T3 | 有效 Discussion URL | `issue2md https://github.com/.../discussions/78` | 输出完整 Markdown，type=discussion |
| T4 | 输出到文件 | `issue2md <url> output.md` | 创建 output.md 文件 |
| T5 | 启用 Reactions | `issue2md -enable-reactions <url>` | Frontmatter 和评论包含 Reactions 统计 |
| T6 | 启用用户链接 | `issue2md -enable-user-links <url>` | @username 渲染为链接 |
| T7 | 私有仓库 + Token | `GITHUB_TOKEN=xxx issue2md <private_url>` | 成功获取内容 |
| T8 | 无效 URL | `issue2md https://example.com/not-github` | stderr 错误，退出码 1 |
| T9 | 资源不存在 | `issue2md https://github.com/.../issues/999999` | stderr "Resource not found"，退出码 1 |
| T10 | 嵌套评论 | Issue with nested replies | 正确渲染引用块层级 |
| T11 | PR Review Comment | PR with file comments | 显示文件路径和行号 |
| T12 | Discussion Answer | Discussion with accepted answer | 显示 ✅ 标记 |

### 4.2 格式验证用例

| ID | 验证项 | 检查方式 |
|----|--------|----------|
| F1 | YAML Frontmatter 存在 | 输出以 `---` 开头和结尾 |
| F2 | 必需字段完整 | title, url, type, author, created_at 均存在 |
| F3 | 代码块语言标记 | 保留原始语言（如 python, go） |
| F4 | 图片链接 | GitHub CDN 链接保持不变 |
| F5 | 时间格式 | ISO 8601 格式 (UTC) |
| F6 | 评论时间排序 | 严格按时间正序 |

---

## 5. 输出格式示例

### 5.1 Issue 完整示例

```yaml
---
title: "[Issue #123] Fix memory leak in data processor"
url: "https://github.com/example/project/issues/123"
type: "issue"
number: 123
author: "johndoe"
author_url: "https://github.com/johndoe"
created_at: "2024-01-15T10:30:00Z"
updated_at: "2024-01-16T14:20:00Z"
status: "closed"
labels: ["bug", "high-priority"]
reactions:
  thumbs_up: 8
  thumbs_down: 0
  laugh: 0
  hooray: 2
  confused: 0
  heart: 5
  rocket: 0
  eyes: 1
---
```

```markdown
# [Issue #123] Fix memory leak in data processor

**作者:** @johndoe | **创建时间:** 2024-01-15 10:30:00 UTC | **状态:** Closed

**标签:** bug, high-priority

---

## 描述

发现数据处理器在处理大型文件时存在内存泄漏问题。经过分析，问题出在缓冲区未正确释放。

**复现步骤：**
1. 加载 1GB+ 的数据文件
2. 执行数据处理
3. 观察内存持续增长

```python
# 问题代码示例
def process_data(file_path):
    buffer = []
    with open(file_path) as f:
        for line in f:
            buffer.append(line)  # 未释放
    return buffer
```

## 评论 (按时间正序)

### @alice (2024-01-15 12:00:00 UTC)

我也能复现这个问题。建议使用生成器替代列表：

```python
def process_data(file_path):
    with open(file_path) as f:
        for line in f:
            yield line
```

> ### @johndoe (2024-01-15 12:30:00 UTC)
>
> 好主意！但是我们需要向后兼容旧的 API。

> > ### @alice (2024-01-15 13:00:00 UTC)
> >
> > 那可以添加一个参数控制行为。

### @bob (2024-01-15 14:00:00 UTC)

**Reactions:** 👍 3, ❤️ 1

我可以帮忙修复这个问题，预计今晚提交 PR。

### @johndoe (2024-01-16 10:00:00 UTC)

已修复，请 review #124。

---

**生成于:** issue2md v1.0.0 | **来源:** https://github.com/example/project/issues/123
```

### 5.2 Pull Request 完整示例

```yaml
---
title: "[PR #456] Refactor authentication module"
url: "https://github.com/example/project/pull/456"
type: "pull_request"
number: 456
author: "janedoe"
author_url: "https://github.com/janedoe"
created_at: "2024-01-10T09:00:00Z"
updated_at: "2024-01-12T16:30:00Z"
status: "merged"
labels: ["refactor", "breaking-change"]
---
```

```markdown
# [PR #456] Refactor authentication module

**作者:** @janedoe | **创建时间:** 2024-01-10 09:00:00 UTC | **状态:** Merged

**标签:** refactor, breaking-change

---

## 描述

重构了认证模块，主要变更：
- 移除过时的 OAuth 1.0 支持
- 统一错误处理
- 添加单元测试

**Breaking Change:** 需要更新环境变量配置。

## 评论 (按时间正序)

### @reviewer1 (2024-01-10 10:00:00 UTC) [Review Comment]

**File:** `src/auth/oauth.py:45`

建议重命名这个函数为 `authenticate_user`，更清晰。

> ### @janedoe (2024-01-10 10:15:00 UTC)
>
> 同意，已修改。

### @reviewer2 (2024-01-10 11:00:00 UTC)

LGTM! 合并后记得更新文档。

### @janedoe (2024-01-12 14:00:00 UTC)

已更新 README.md，可以合并了。

---

**生成于:** issue2md v1.0.0 | **来源:** https://github.com/example/project/pull/456
```

### 5.3 Discussion 完整示例

```yaml
---
title: "[Discussion #78] Best practices for error handling?"
url: "https://github.com/example/project/discussions/78"
type: "discussion"
number: 78
author: "newuser"
author_url: "https://github.com/newuser"
created_at: "2024-01-05T08:00:00Z"
updated_at: "2024-01-08T18:00:00Z"
status: "open"
---
```

```markdown
# [Discussion #78] Best practices for error handling?

**作者:** @newuser | **创建时间:** 2024-01-05 08:00:00 UTC | **状态:** Open

---

## 描述

刚接触这个项目，想了解一下项目中错误处理的最佳实践。我应该使用自定义异常类还是内置的异常类型？

## 评论 (按时间正序)

### @senior-dev (2024-01-05 09:00:00 UTC)

我们使用自定义异常类，定义在 `src/exceptions.py`：

```python
class ProjectError(Exception):
    """Base exception for all project errors."""
    pass

class ValidationError(ProjectError):
    """Raised when input validation fails."""
    pass
```

这样可以在上层统一捕获和处理。

### @newuser (2024-01-05 09:30:00 UTC)

非常感谢！那日志记录有什么建议吗？

> ### @senior-dev (2024-01-05 10:00:00 UTC)
>
> 我们使用 Python 标准库的 `logging` 模块。配置在 `src/logging_config.py`。

### @contributor (2024-01-08 15:00:00 UTC) ✅ [Accepted Answer]

总结一下最佳实践：

1. **自定义异常**：继承 `ProjectError` 基类
2. **错误传递**：使用 `raise ... from ...` 保留原始错误
3. **日志记录**：在处理错误的边界层记录日志
4. **用户友好**：向用户展示友好的错误消息，技术细节记录到日志

详细的错误处理指南请参考：[CONTRIBUTING.md - Error Handling](https://github.com/example/project/blob/main/CONTRIBUTING.md#error-handling)

---

**生成于:** issue2md v1.0.0 | **来源:** https://github.com/example/project/discussions/78
```

