# HONGS 的个人博客

由 Flask 自建的个人博客:仓库内的 Markdown 文件是内容的唯一数据源,
push 到 master 后服务器通过 Webhook 自动拉取并重启,文章即上线。

领域术语见 [CONTEXT.md](./CONTEXT.md),完整设计与部署手册见 [DEVELOPMENT.md](./DEVELOPMENT.md),
文章解析规则见 [docs/ARTICLES.md](./docs/ARTICLES.md)。

## 功能

- 卡片式首页,按日期倒序,每页 10 篇
- 文章页:`/posts/<slug>/`,代码高亮(Pygments)+ 一键复制按钮
- 深色模式:右上角手动切换,localStorage 记忆
- Sites 页:`/sites/`,自有站点导航(数据来自 `content/sites.yaml`)
- 关于页:`/about/`
- 草稿:frontmatter 标记 `draft: true` 的文章全环境不渲染
- 页脚展示「本站已运行 N 天」
- 后台管理:`/admin/`,初始密码 `admin`(**上线务必在后台改掉或用环境变量 `ADMIN_PASSWORD` 覆盖**),可写文章/存草稿/删文章/维护 Sites 列表/修改密码
- SEO 基础:meta description、canonical、`/sitemap.xml`、`/robots.txt`
- GitHub Webhook 自动部署(HMAC-SHA256 签名校验)

## 快速开始

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt   # Linux/macOS: .venv/bin/pip
.venv\Scripts\python wsgi.py                    # 开发服务器 http://127.0.0.1:5000/
```

运行测试:

```bash
.venv\Scripts\python -m pytest tests -q
```

## 写文章

在 `content/posts/` 下新建 `<slug>.md`:

```markdown
---
title: 文章标题        # 必填
date: 2026-08-26      # 必填
description: 一句话摘要 # 可选,缺省自动截取正文开头
draft: true           # 可选,true 时不渲染
---

正文 Markdown……
```

- slug 即文件名,手写英文,发布后不要修改(URL 永久绑定)
- 未写完就加 `draft: true`,可以随时 push

## 项目结构

```
app/            Flask 应用(工厂、内容层、路由、模板、静态资源)
content/        文章、关于页、Sites 数据(唯一数据源)
deploy/         systemd 单元与 nginx 配置模板
scripts/         Pygments 双主题 CSS 生成脚本
tests/          pytest 冒烟测试
```

## 部署

目标环境:Linux + nginx + gunicorn + systemd,一次性操作步骤见
[DEVELOPMENT.md 第 5 节](./DEVELOPMENT.md#5-部署手册服务器一次性操作)。

日常发布只需:

```bash
git push origin master
```
