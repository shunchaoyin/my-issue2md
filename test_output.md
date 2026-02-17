---
title: "[Issue #12345] bpo-36127: Fix _PyArg_UnpackKeywords() warning"
url: "https://github.com/python/cpython/issues/12345"
type: "Issue"
number: 12345
author: "vstinner"
author_url: "https://github.com/vstinner"
created_at: "2019-03-15T14:03:40Z"
updated_at: "2019-03-18T17:39:27Z"
status: "closed"
labels: ["skip news"]
---
# [Issue #12345] bpo-36127: Fix _PyArg_UnpackKeywords() warning

**作者:** @vstinner | **创建时间:** 2019-03-15T14:03:40Z UTC | **状态:** Closed
**标签:** skip news

---

## 描述

Use Py_ssize_t type rather than int for the 'i' variable.

<!-- issue-number: [bpo-36127](https://bugs.python.org/issue36127) -->
https://bugs.python.org/issue36127
<!-- /issue-number -->


## 评论 (按时间正序)

### @vstinner (2019-03-15T14:04:09Z UTC)

This change fix the following warning on Windows:

```
c:\projects\cpython\python\getargs.c(2425): warning C4244: '=': conversion from 'Py_ssize_t' to 'int', possible loss of data [C:\projects\cpython\PCbuild\pythoncore.vcxproj]
```

@serhiy-storchaka: Would you mind to review this change?

### @serhiy-storchaka (2019-03-15T14:13:39Z UTC)

I do not think this is the best way to fix this warning. All corresponding variables except `nargs` have type `int`, and I want to preserve this.

### @vstinner (2019-03-15T14:23:20Z UTC)

> I do not think this is the best way to fix this warning. All corresponding variables except nargs have type int, and I want to preserve this.

Why is it wrong to use Py_ssize_t for 'i'?

I don't want to use Py_ssize_t for other variables, since _PyParser uses int.

Feel free to fix the warning differently. I only worry of having no compiler warning on Windows :-)

### @vstinner (2019-03-18T17:39:19Z UTC)

Serhiy wrote a diffrent fix:  PR #12353.

---

**生成于:** issue2md v0.1.0 | **来源:** https://github.com/python/cpython/issues/12345
