import pytest

from app import create_app

POST = (
    "---\n"
    "title: 测试文章\n"
    "date: 2026-01-01\n"
    "---\n"
    "\n"
    "正文内容\n"
    "\n"
    "```python\n"
    'print("hi")\n'
    "```\n"
)

DRAFT = (
    "---\n"
    "title: 草稿文章\n"
    "date: 2026-02-01\n"
    "draft: true\n"
    "---\n"
    "\n"
    "草稿内容\n"
)


@pytest.fixture()
def client(tmp_path):
    content = tmp_path / "content"
    (content / "posts").mkdir(parents=True)
    (content / "posts" / "test-post.md").write_text(POST, encoding="utf-8")
    (content / "posts" / "draft-post.md").write_text(DRAFT, encoding="utf-8")
    (content / "about.md").write_text(
        "---\ntitle: 关于\n---\n关于我\n", encoding="utf-8"
    )
    (content / "sites.yaml").write_text(
        "sites:\n  - name: GitHub\n    url: https://github.com/BYHONGS\n"
        "    description: code\n",
        encoding="utf-8",
    )
    app = create_app(
        {
            "CONTENT_DIR": content,
            "WEBHOOK_SECRET": "test-secret",
            "PASSWORD_FILE": tmp_path / ".admin_password",
        }
    )
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client
