def login(client, password="admin"):
    return client.post("/admin/login", data={"password": password})


def test_admin_requires_login(client):
    resp = client.get("/admin/")
    assert resp.status_code == 302
    assert "/admin/login" in resp.headers["Location"]


def test_login_wrong_password(client):
    resp = login(client, password="wrong")
    html = resp.get_data(as_text=True)
    assert resp.status_code == 200
    assert "密码错误" in html


def test_login_and_dashboard(client):
    resp = login(client)
    assert resp.status_code == 302
    resp = client.get("/admin/")
    html = resp.get_data(as_text=True)
    assert resp.status_code == 200
    assert "测试文章" in html
    assert "草稿文章" in html
    assert "草稿" in html


def test_create_post_visible_publicly(client):
    login(client)
    resp = client.post(
        "/admin/posts/new",
        data={
            "slug": "brand-new",
            "title": "全新文章",
            "date": "2026-03-15",
            "description": "摘要",
            "body": "新文章正文",
        },
    )
    assert resp.status_code == 302
    assert client.get("/posts/brand-new/").status_code == 200
    assert "/posts/brand-new/" in client.get("/sitemap.xml").get_data(as_text=True)


def test_create_draft_hidden_publicly(client):
    login(client)
    client.post(
        "/admin/posts/new",
        data={
            "slug": "secret-draft",
            "title": "秘密草稿",
            "date": "2026-03-16",
            "draft": "on",
            "body": "草稿正文",
        },
    )
    assert client.get("/posts/secret-draft/").status_code == 404
    assert "秘密草稿" in client.get("/admin/").get_data(as_text=True)


def test_create_post_rejects_bad_slug(client):
    login(client)
    resp = client.post(
        "/admin/posts/new",
        data={"slug": "Bad Slug!", "title": "T", "date": "2026-03-15", "body": "B"},
    )
    html = resp.get_data(as_text=True)
    assert resp.status_code == 200
    assert "slug 只能是小写字母" in html
    assert client.get("/posts/Bad%20Slug!/").status_code == 404


def test_edit_post(client):
    login(client)
    resp = client.post(
        "/admin/posts/test-post/edit",
        data={
            "title": "改名后的文章",
            "date": "2026-01-02",
            "body": "修改后的正文",
        },
    )
    assert resp.status_code == 302
    html = client.get("/posts/test-post/").get_data(as_text=True)
    assert "改名后的文章" in html
    assert "修改后的正文" in html


def test_delete_post(client):
    login(client)
    resp = client.post("/admin/posts/test-post/delete")
    assert resp.status_code == 302
    assert client.get("/posts/test-post/").status_code == 404


def test_sites_add_and_delete(client):
    login(client)
    resp = client.post(
        "/admin/sites",
        data={"name": "新站", "url": "https://new.example.com", "description": "d"},
    )
    assert resp.status_code == 302
    assert "新站" in client.get("/sites/").get_data(as_text=True)

    resp = client.post(
        "/admin/sites",
        data={"name": "重复", "url": "https://new.example.com"},
        follow_redirects=True,
    )
    assert "该 URL 已存在" in resp.get_data(as_text=True)

    resp = client.post("/admin/sites/delete", data={"url": "https://new.example.com"})
    assert resp.status_code == 302
    assert "新站" not in client.get("/sites/").get_data(as_text=True)


def test_logout(client):
    login(client)
    assert client.get("/admin/logout").status_code == 302
    assert client.get("/admin/").status_code == 302


def test_change_password_and_relogin(client):
    login(client)
    resp = client.post(
        "/admin/password",
        data={
            "current_password": "admin",
            "new_password": "newpass123",
            "confirm_password": "newpass123",
        },
    )
    assert resp.status_code == 302

    client.get("/admin/logout")
    assert login(client, password="admin").get_data(as_text=True).find("密码错误") != -1
    assert login(client, password="newpass123").status_code == 302
    assert client.get("/admin/").status_code == 200


def test_change_password_requires_correct_current(client):
    login(client)
    resp = client.post(
        "/admin/password",
        data={
            "current_password": "wrong",
            "new_password": "newpass123",
            "confirm_password": "newpass123",
        },
        follow_redirects=True,
    )
    assert "当前密码错误" in resp.get_data(as_text=True)
    assert login(client, password="admin").status_code == 302


def test_change_password_rejects_mismatch(client):
    login(client)
    resp = client.post(
        "/admin/password",
        data={
            "current_password": "admin",
            "new_password": "newpass123",
            "confirm_password": "different",
        },
        follow_redirects=True,
    )
    assert "两次输入的新密码不一致" in resp.get_data(as_text=True)
    assert login(client, password="admin").status_code == 302


def test_change_password_rejects_short(client):
    login(client)
    resp = client.post(
        "/admin/password",
        data={
            "current_password": "admin",
            "new_password": "abc",
            "confirm_password": "abc",
        },
        follow_redirects=True,
    )
    assert "新密码至少 6 位" in resp.get_data(as_text=True)
