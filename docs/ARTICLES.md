# 文章解析说明

一篇文章 = `content/posts/` 下的一个 `.md` 文件,UTF-8 编码。
解析入口:`app/content.py` 的 `load_posts()`,在应用启动时(`create_app`)执行一次。

## 解析流程

```
扫描 content/posts/*.md
  → 解析 Frontmatter(YAML)
  → draft: true ? 丢弃 : 继续
  → 提取 title / date / description(缺省则回退)
  → 正文 Markdown → HTML(mistune + Pygments)
  → 按 date 倒序放入内存缓存
```

无数据库、无热更新:修改文章后需重启进程才会重新解析
(线上由 Webhook 自动 `systemctl restart`,本地手动重启开发服务器)。

## Frontmatter 字段

| 字段 | 必填 | 类型 | 缺省行为 |
|---|---|---|---|
| `title` | 是 | 字符串 | 回退为 slug |
| `date` | 是 | `YYYY-MM-DD`(YAML 日期或 ISO 字符串) | 回退为今天 |
| `description` | 否 | 字符串 | 自动截取正文前 120 字(规则见下) |
| `draft` | 否 | 布尔 | `true` 时整篇丢弃:不渲染、404、不进列表 |

## 摘要自动生成(`excerpt()`)

当 frontmatter 没有写 `description` 时:

1. 先删除所有 ``` 围栏代码块
2. 去除 Markdown 标记字符(`# > * \` ~ [ ] !`)
3. 拼接所有非空行,取前 120 字

首页卡片显示手写 description 或该自动摘要。

## Markdown 渲染(`app/markdown.py`)

- 引擎:mistune 3,启用插件:**表格、删除线(`~~xx~~`)、脚注**
- 代码块:标注语言则用 Pygments 高亮(样式见 `static/css/pygments-*.css`,
  由 `scripts/generate_pygments_css.py` 生成);未标注或未知语言则输出纯文本代码块
- 原始 HTML 直通(内容源是自己的仓库,不做转义)

````markdown
```python
def hello():
    print("你好,世界")   # → Pygments 高亮 + 复制按钮
```
````

## Slug 与 URL

- 文件名(不含 `.md`)即 slug:`content/posts/hello-world.md` → `/posts/hello-world/`
- 手写英文短标识;**发布后不可改名**,否则 URL 断链
- 首页列表按 `date` 倒序,每页 10 篇(`config.py` 的 `POSTS_PER_PAGE`)

## 其他被解析的内容

| 文件 | 解析方式 |
|---|---|
| `content/about.md` | 同一渲染管道,仅取正文;frontmatter 可省略 |
| `content/sites.yaml` | `sites` 列表,每条 `name` / `url` / `description`,缺省字段补空值 |

## 最小示例

```markdown
---
title: 我的第一篇文章
date: 2026-08-26
description: 手写摘要会优先于自动截取。
---

## 小标题

正文支持 **加粗**、[链接](https://example.com)、表格与脚注[^1]。

[^1]: 脚注内容。
```
