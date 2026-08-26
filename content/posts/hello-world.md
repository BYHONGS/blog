---
title: 你好,世界
date: 2026-08-26
description: 博客的第一篇文章:为什么自建这个站,以及它现在的样子。
---

## 为什么自建

与其把文章托管在别人的平台,不如用一个 Markdown 仓库做唯一数据源:
写完 push,服务器自动拉取重启,文章就上线了。

整个站点是 Flask 自建的,没有数据库——启动时扫描 `content/posts/` 目录,
解析 frontmatter 后缓存在内存里。

## 它支持什么

- 深色模式(右上角按钮手动切换)
- 代码高亮和一键复制:

```python
def hello():
    print("你好,世界")
```

- 卡片式首页与分页

## 写作约定

每篇文章是一个 `content/posts/<slug>.md`,slug 手写英文、发布后不再修改。
未写完的加上 `draft: true` 就可以放心 push。

欢迎常来。
