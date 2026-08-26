import hashlib
import hmac


def _sign(secret, body):
    return (
        "sha256="
        + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    )


def test_index_lists_posts(client):
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "测试文章" in html
    assert "草稿文章" not in html
    assert "本站已运行" in html


def test_post_page_renders(client):
    resp = client.get("/posts/test-post/")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "正文内容" in html
    assert "highlight" in html


def test_draft_post_is_404(client):
    assert client.get("/posts/draft-post/").status_code == 404


def test_about_page(client):
    resp = client.get("/about/")
    assert resp.status_code == 200
    assert "关于我" in resp.get_data(as_text=True)


def test_sites_page(client):
    resp = client.get("/sites/")
    html = resp.get_data(as_text=True)
    assert resp.status_code == 200
    assert "GitHub" in html
    assert 'rel="noopener noreferrer"' in html


def test_pagination_out_of_range_is_404(client):
    assert client.get("/?page=99").status_code == 404
    assert client.get("/?page=0").status_code == 404


def test_webhook_rejects_bad_signature(client):
    resp = client.post("/api/webhook", json={"ref": "refs/heads/master"})
    assert resp.status_code == 403


def test_webhook_ping_ok(client):
    body = b'{"zen": "Keep it simple."}'
    resp = client.post(
        "/api/webhook",
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": _sign("test-secret", body),
        },
    )
    assert resp.status_code == 200


def test_webhook_non_master_ref_ignored(client):
    body = b'{"ref": "refs/heads/feature"}'
    resp = client.post(
        "/api/webhook",
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": _sign("test-secret", body),
        },
    )
    assert resp.status_code == 200


def test_webhook_valid_push_accepted(client, monkeypatch):
    calls = []
    monkeypatch.setattr("app.routes.webhook._deploy", lambda *a: calls.append(a))
    body = b'{"ref": "refs/heads/master"}'
    resp = client.post(
        "/api/webhook",
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": _sign("test-secret", body),
        },
    )
    assert resp.status_code == 202


def test_post_page_has_meta_description_and_canonical(client):
    html = client.get("/posts/test-post/").get_data(as_text=True)
    assert '<meta name="description"' in html
    assert 'rel="canonical"' in html
    assert "正文内容" in html


def test_sitemap_lists_posts(client):
    resp = client.get("/sitemap.xml")
    assert resp.status_code == 200
    assert resp.mimetype == "application/xml"
    xml = resp.get_data(as_text=True)
    assert "/posts/test-post/" in xml
    assert "draft-post" not in xml
    assert "/sites/" in xml


def test_robots_references_sitemap(client):
    resp = client.get("/robots.txt")
    assert resp.status_code == 200
    assert "Sitemap: http://localhost/sitemap.xml" in resp.get_data(as_text=True)
