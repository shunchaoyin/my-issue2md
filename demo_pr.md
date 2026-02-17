---
title: "[PR #12353] bpo-36127: Fix compiler warning in _PyArg_UnpackKeywords()."
url: "https://github.com/python/cpython/pull/12353"
type: "PR"
number: 12353
author: "serhiy-storchaka"
author_url: "https://github.com/serhiy-storchaka"
created_at: "2019-03-15T16:00:56Z"
updated_at: "2019-03-18T13:38:26Z"
status: "merged"
labels: ["skip news"]
---
# [PR #12353] bpo-36127: Fix compiler warning in _PyArg_UnpackKeywords().

**作者:** @serhiy-storchaka | **创建时间:** 2019-03-15T16:00:56Z UTC | **状态:** Merged
**标签:** skip news

---

## 描述

Since `nargs <= maxpos`, `nargs` can be casted to `int` without lost.

<!-- issue-number: [bpo-36127](https://bugs.python.org/issue36127) -->
https://bugs.python.org/issue36127
<!-- /issue-number -->


## 评论 (按时间正序)

### @vstinner (2019-03-18T13:38:25Z UTC) [Review Comment]

**File:** `Python/getargs.c:2425`

I'm not sure that this code is safe is nargs > INT_MAX. (int)(INT_MAX+1) gives 0, no?

Maybe write something like:

```
i = (nargs < INT_MAX) ? (int)nargs : INT_MAX;
i = Py_MAX(i, posonly);
```

---

**生成于:** issue2md v0.1.0 | **来源:** https://github.com/python/cpython/pull/12353
