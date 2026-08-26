import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

import frontmatter
import yaml

from .markdown import render_markdown

EXCERPT_LENGTH = 120


@dataclass(frozen=True)
class Post:
    slug: str
    title: str
    date: date
    description: str
    html: str
    draft: bool = False


def _to_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def excerpt(text, limit=EXCERPT_LENGTH):
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"[#>*`~\[\]!]", "", text)
    lines = (line.strip() for line in text.splitlines())
    joined = "".join(line for line in lines if line)
    return joined[:limit]


def valid_slug(slug):
    return bool(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug))


def load_posts(content_dir, include_drafts=False):
    posts = []
    posts_dir = Path(content_dir) / "posts"
    if not posts_dir.is_dir():
        return posts
    for path in sorted(posts_dir.glob("*.md")):
        post = frontmatter.load(path)
        if post.metadata.get("draft") and not include_drafts:
            continue
        posts.append(
            Post(
                slug=path.stem,
                title=str(post.metadata.get("title") or path.stem),
                date=_to_date(post.metadata.get("date") or date.today()),
                description=post.metadata.get("description") or excerpt(post.content),
                html=render_markdown(post.content),
                draft=bool(post.metadata.get("draft")),
            )
        )
    posts.sort(key=lambda p: p.date, reverse=True)
    return posts


def load_post_raw(content_dir, slug):
    if not valid_slug(slug):
        return None
    path = Path(content_dir) / "posts" / f"{slug}.md"
    if not path.exists():
        return None
    post = frontmatter.load(path)
    return {
        "slug": slug,
        "title": str(post.metadata.get("title") or slug),
        "date": _to_date(post.metadata.get("date") or date.today()),
        "description": post.metadata.get("description") or "",
        "draft": bool(post.metadata.get("draft")),
        "body": post.content,
    }


def save_post(content_dir, slug, title, date_value, description="", draft=False, body=""):
    meta = {"title": title, "date": date_value}
    if description:
        meta["description"] = description
    if draft:
        meta["draft"] = True
    fm = yaml.safe_dump(
        meta, allow_unicode=True, sort_keys=False, default_flow_style=False
    ).rstrip("\n")
    path = Path(content_dir) / "posts" / f"{slug}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{fm}\n---\n\n{body.strip()}\n", encoding="utf-8")
    return path


def delete_post(content_dir, slug):
    if not valid_slug(slug):
        return False
    path = Path(content_dir) / "posts" / f"{slug}.md"
    if not path.exists():
        return False
    path.unlink()
    return True


def save_sites(content_dir, sites):
    path = Path(content_dir) / "sites.yaml"
    path.write_text(
        yaml.safe_dump({"sites": sites}, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return path


def load_about(content_dir):
    path = Path(content_dir) / "about.md"
    if not path.exists():
        return ""
    return render_markdown(frontmatter.load(path).content)


def load_sites(content_dir):
    path = Path(content_dir) / "sites.yaml"
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    sites = data.get("sites", [])
    for site in sites:
        site.setdefault("name", "")
        site.setdefault("url", "#")
        site.setdefault("description", "")
    return sites


def load_site_content(content_dir):
    content_dir = Path(content_dir)
    return {
        "posts": load_posts(content_dir),
        "about_html": load_about(content_dir),
        "sites": load_sites(content_dir),
    }
