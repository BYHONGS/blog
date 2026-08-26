# HONGS 博客 · 开发文档

个人博客,Flask 自建,仓库内 Markdown 为唯一数据源,部署在自有 Linux 服务器。
术语定义见 [CONTEXT.md](./CONTEXT.md)(Post、Slug、Draft、Sites 页)。

## 1. 已定决策

| 维度 | 决策 |
|---|---|
| 内容 | 纯中文;技术+生活混合 |
| 内容管理 | 仓库内 Markdown,push 即发布 |
| 技术栈 | Python + Flask + Jinja2,无数据库 |
| 页面 | 首页(卡片分页)、文章页 `/posts/{slug}/`、关于页 `/about/`、Sites 页 `/sites/` |
| 功能 | 深色模式(仅手动切换)、代码块复制按钮、页脚展示已运行时间、SEO 基础(meta description/canonical/sitemap/robots)、后台管理(密码登录,写作+Sites 维护) |
| 明确不做(v1) | RSS、标签、归档、搜索、评论 |
| 视觉 | 卡片式现代风:圆角、阴影、hover 抬升 |
| 托管 | GitHub `BYHONGS/blog`,master 分支 |
| 部署 | Linux 服务器,nginx 反代 + gunicorn + systemd,暂用 IP 直访 |

## 2. 内容规范

### 2.1 目录

```
content/
├── posts/          # 所有 Post,<slug>.md
├── about.md        # 关于页正文(同渲染管道,无 date/draft 要求)
└── sites.yaml      # Sites 页数据
```

### 2.2 Frontmatter

```yaml
---
title: 文章标题          # 必填
date: 2026-08-26        # 必填,列表排序依据
description: 一句话摘要   # 可选;缺省自动截取正文前 120 字
draft: true             # 可选;true 时全环境不渲染、不进列表
---
```

### 2.3 Slug 规则

- 手写英文短标识,即文件名:`hello-world.md` → `/posts/hello-world/`
- **发布后不可变更**,否则外链断裂
- 正文 Markdown,代码块标注语言以获得高亮

### 2.4 sites.yaml

```yaml
sites:
  - name: 我的 GitHub
    url: https://github.com/BYHONGS
    description: 代码都在这里
```

## 3. 项目结构

```
blog/
├── app/
│   ├── __init__.py        # create_app() 工厂;启动时加载内容
│   ├── content.py         # 扫描 content/,解析 frontmatter,内存缓存
│   ├── markdown.py        # 渲染管道:mistune + Pygments
│   ├── routes/
│   │   ├── main.py        # 页面路由
│   │   └── webhook.py     # POST /api/webhook
│   ├── templates/
│   │   ├── base.html      # 布局:顶栏导航(首页/关于/Sites)+深色开关
│   │   ├── index.html     # 卡片网格 + 上/下页
│   │   ├── post.html      # 文章页(标题、日期、正文)
│   │   ├── about.html
│   │   └── sites.html
│   └── static/
│       ├── css/style.css  # CSS 变量双主题
│       └── js/main.js     # 深色切换、代码复制
├── content/               # 见第 2 节
├── deploy/
│   ├── blog.service       # systemd 单元模板
│   └── nginx.conf         # nginx 站点配置模板
├── config.py              # 从环境变量读 SECRET_KEY / WEBHOOK_SECRET
├── wsgi.py                # gunicorn 入口:app:create_app()
├── tests/                 # pytest:路由冒烟 + draft 不可见
├── requirements.txt       # flask, gunicorn, mistune, pygments, python-frontmatter, pyyaml, pytest
├── CONTEXT.md
└── DEVELOPMENT.md
```

## 4. 核心设计

### 4.1 内容加载(content.py)

- `create_app()` 时一次性扫描 `content/posts/*.md`,解析出 `Post(title, slug, date, description, html)` 列表,Draft 直接丢弃,按 date 倒序存于 app extensions
- 无数据库;内容更新 = webhook 重启进程后重新扫描
- 提供 `get_post(slug)`、`get_page(n)`(每页 10 篇)

### 4.2 路由

| 方法 | 路径 | 行为 |
|---|---|---|
| GET | `/` | 卡片列表,`?page=N`(缺省 1),越界 404 |
| GET | `/posts/<slug>/` | 文章页;不存在 404(Draft 在加载层已剔除) |
| GET | `/about/` | 渲染 `about.md` |
| GET | `/sites/` | 渲染 sites.yaml 列表,条目为新窗口外链 |
| POST | `/api/webhook` | 接收 GitHub Webhook |
| GET/POST | `/admin/login` | 密码登录(初始 `admin`,生产用 `ADMIN_PASSWORD` 覆盖) |
| GET | `/admin/` | 后台首页:全部 Post(含草稿)+ Sites 列表 |
| GET/POST | `/admin/posts/new`、`/admin/posts/<slug>/edit` | 写作/编辑表单,slug 创建后锁定 |
| POST | `/admin/posts/<slug>/delete`、`/admin/sites`、`/admin/sites/delete` | 删除文章、增删 Sites 条目 |
| GET/POST | `/admin/password` | 修改后台密码(需当前密码) |
| GET | `/admin/logout` | 退出登录 |

### 4.3 后台管理(routes/admin.py)

- 会话认证:`session["admin"]`,密码用 werkzeug 哈希恒时校验;Cookie `SameSite=Lax` + `HttpOnly`;后台页面 `noindex`
- 密码存储:werkzeug 哈希存于 `.admin_password`(已 gitignore,不入库);`ADMIN_PASSWORD` 环境变量仅作首次引导,后台修改后以文件为准
- 保存 = 写回 `content/` 文件(与手写文件完全同构)→ 立即重载内存缓存,前台即刻生效
- **gunicorn 必须单 worker**(blog.service 已注明):缓存重载只发生在处理请求的进程内,多 worker 会出现数据不一致
- slug 校验 `^[a-z0-9]+(-[a-z0-9]+)*$`,杜绝路径穿越;编辑时 slug 只读(发布后不可变)

### 4.4 Webhook(webhook.py)

1. 校验 `X-Hub-Signature-256`(HMAC-SHA256,body 为原文,密钥 `WEBHOOK_SECRET`),失败返回 403
2. 仅处理 `push` 事件且 `ref == refs/heads/master`
3. 子进程执行 `git -C /srv/blog pull`,成功后触发 `sudo systemctl restart blog`(受限 sudoers 白名单),响应立即返回 202

### 4.5 前端

- **双主题**:`:root` 定义亮色 CSS 变量,`[data-theme="dark"]` 覆盖为暗色;不做 `prefers-color-scheme`,仅顶栏按钮切换,选择写入 `localStorage`
- **代码复制**:JS 为每个 `pre` 注入右上角按钮,`navigator.clipboard.writeText`,成功后短暂显示「已复制」
- **卡片**:响应式网格(窄屏单列),含标题、日期(`YYYY-MM-DD`)、摘要(description 优先,回退自动截取);圆角 + 细阴影 + hover 轻微上浮
- **页脚**:`© {年份} HONGS · 本站已运行 N 天`,天数 = 今天 − `SITE_LAUNCH_DATE`(config.py,当前为开站日 2026-08-26)
- **SEO**:每页 `<meta name="description">`(文章页用 description/摘要)与 canonical;`/sitemap.xml` 列出全部 Post 及固定页;`/robots.txt` 指向 sitemap;`ProxyFix` 信任 nginx 的 `X-Forwarded-*` 以生成正确外链
- 中文字体栈优先,正文行高 ≥ 1.8

## 5. 部署手册(服务器一次性操作)

前提:Linux + Python ≥ 3.10,域名未就绪,80 端口可达。

```bash
# 1. 基础依赖
sudo apt install nginx git python3-venv

# 2. 拉代码 + 环境
sudo mkdir -p /srv/blog && sudo chown $USER /srv/blog
git clone git@github.com:BYHONGS/blog.git /srv/blog
cd /srv/blog && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

# 3. 密钥(生成后写入环境;ADMIN_PASSWORD 务必改掉初始值)
echo "WEBHOOK_SECRET=$(openssl rand -hex 32)" >> /srv/blog/.env
echo "SECRET_KEY=$(openssl rand -hex 32)"   >> /srv/blog/.env
echo "ADMIN_PASSWORD=$(openssl rand -hex 16)" >> /srv/blog/.env

# 4. systemd:deploy/blog.service 里 EnvironmentFile=/srv/blog/.env
sudo cp deploy/blog.service /etc/systemd/system/
sudo systemctl enable --now blog

# 5. nginx:反代 127.0.0.1:8000
sudo cp deploy/nginx.conf /etc/nginx/sites-available/blog
sudo ln -s /etc/nginx/sites-available/blog /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# 6. 允许服务账号免密重启自己(仅这一条命令)
echo "hongs ALL=(root) NOPASSWD: /usr/bin/systemctl restart blog" | \
  sudo tee /etc/sudoers.d/blog-restart

# 7. 防火墙放行 80
sudo ufw allow 80/tcp
```

GitHub 侧:仓库 Settings → Webhooks → `http://<服务器IP>/api/webhook`,
Content type `application/json`,Secret 与 `.env` 中一致,事件选 push。

## 6. 发布流程(日常)

```
写 content/posts/<slug>.md → git add/commit/push
→ Webhook 自动 pull 并重启 → 新文上线
```

写一半的文章加 `draft: true` 可以随时 push,不会被渲染。

## 7. 验收清单

- [ ] 首页卡片按日期倒序,每页 10 篇,上下页可用
- [ ] `/posts/{slug}/` 正常渲染,代码高亮 + 复制按钮工作
- [ ] `draft: true` 的文章在任何页面不可见
- [ ] 深色切换即时生效且刷新后保持
- [ ] 页脚显示「本站已运行 N 天」且天数正确
- [ ] `/sites/` 与 sites.yaml 数据一致,新窗口打开外链
- [ ] push 后无需登录服务器,约 30 秒内线上生效
- [ ] `/admin/login` 初始密码可登录;后台发文/草稿/删文、Sites 增删即时生效
- [ ] 生产环境 `ADMIN_PASSWORD` 已改为非默认值
