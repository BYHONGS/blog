# 个人博客(HONGS)

一个由 Flask 自建的个人博客,文章以仓库内 Markdown 文件为唯一数据源,部署在自有 Linux 服务器上。

## Language

**Post(文章)**:
`content/posts/` 目录下的一个 Markdown 文件,是博客内容的唯一载体。文件名(不含扩展名)即其 Slug。
_Avoid_: 博文、日志、entry

**Slug**:
作者为每篇 Post 手写的英文短标识,构成该文的永久 URL `/posts/{slug}/`。发布后不可变更,否则断链。
_Avoid_: 文件名、ID、别名

**Frontmatter(元数据)**:
Post 文件头部的 YAML 块,携带 title、date 等结构化信息;不属于正文。

**Draft(草稿)**:
Frontmatter 中标记 `draft: true` 的 Post,在任何环境下都不渲染、不出现在列表中;去掉标记即视为发布。
_Avoid_: 隐藏文章、未发布

**Sites 页**:
汇总展示站长自有个人网站的导航页,路由 `/sites/`,数据来自 `content/sites.yaml`(每条含名称、URL、一句话描述)。
_Avoid_: 友链、链接收藏、书签页

**Uptime(已运行时间)**:
博客自开站日起经过的天数,固定展示在每页页脚。
_Avoid_: 运行时长、进程时间

**后台(Admin)**:
密码登录的管理界面,用于撰写 Post(含 Draft)与维护 Sites 页数据;保存即写回仓库文件并重载内存。
_Avoid_: CMS、控制台
