import re
from datetime import date, datetime
from functools import wraps

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from .. import auth
from ..content import (
    delete_post,
    load_post_raw,
    load_posts,
    load_site_content,
    save_post,
    save_sites,
    valid_slug,
)

bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin.login"))
        return view(*args, **kwargs)

    return wrapped


def _content_dir():
    return current_app.config["CONTENT_DIR"]


def _reload():
    current_app.extensions["content"] = load_site_content(_content_dir())


def _parse_date(value):
    try:
        return datetime.strptime(value.strip(), "%Y-%m-%d").date()
    except (ValueError, AttributeError):
        return None


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password", "")
        if auth.verify(current_app.config, password):
            session["admin"] = True
            return redirect(url_for("admin.dashboard"))
        flash("密码错误")
    return render_template("admin/login.html")


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("admin.login"))


@bp.route("/password", methods=["GET", "POST"])
@admin_required
def change_password():
    if request.method == "POST":
        current = request.form.get("current_password", "")
        new = request.form.get("new_password", "")
        confirm = request.form.get("confirm_password", "")
        if not auth.verify(current_app.config, current):
            flash("当前密码错误")
        elif len(new) < 6:
            flash("新密码至少 6 位")
        elif new != confirm:
            flash("两次输入的新密码不一致")
        else:
            auth.save(current_app.config, new)
            flash("密码已修改")
            return redirect(url_for("admin.dashboard"))
    return render_template("admin/password.html")


@bp.route("/")
@admin_required
def dashboard():
    posts = load_posts(_content_dir(), include_drafts=True)
    sites = current_app.extensions["content"]["sites"]
    return render_template("admin/dashboard.html", posts=posts, sites=sites)


@bp.route("/posts/new", methods=["GET", "POST"])
@admin_required
def post_new():
    if request.method == "POST":
        form = _post_form_from_request()
        error = _validate_post_form(form, existing=None)
        if error:
            flash(error)
            return render_template("admin/post_form.html", post=form, is_new=True)
        save_post(
            _content_dir(),
            slug=form["slug"],
            title=form["title"],
            date_value=form["date"],
            description=form["description"],
            draft=form["draft"],
            body=form["body"],
        )
        _reload()
        flash(f"已发布:{form['title']}" if not form["draft"] else f"已保存草稿:{form['title']}")
        return redirect(url_for("admin.dashboard"))
    return render_template(
        "admin/post_form.html",
        post={
            "slug": "",
            "title": "",
            "date": date.today(),
            "description": "",
            "draft": False,
            "body": "",
        },
        is_new=True,
    )


@bp.route("/posts/<slug>/edit", methods=["GET", "POST"])
@admin_required
def post_edit(slug):
    if not valid_slug(slug):
        abort(404)
    if request.method == "POST":
        form = _post_form_from_request(slug=slug)
        error = _validate_post_form(form, existing=slug)
        if error:
            flash(error)
            return render_template("admin/post_form.html", post=form, is_new=False)
        save_post(
            _content_dir(),
            slug=slug,
            title=form["title"],
            date_value=form["date"],
            description=form["description"],
            draft=form["draft"],
            body=form["body"],
        )
        _reload()
        flash(f"已保存:{form['title']}")
        return redirect(url_for("admin.dashboard"))
    post = load_post_raw(_content_dir(), slug)
    if post is None:
        abort(404)
    return render_template("admin/post_form.html", post=post, is_new=False)


@bp.route("/posts/<slug>/delete", methods=["POST"])
@admin_required
def post_delete(slug):
    if delete_post(_content_dir(), slug):
        _reload()
        flash(f"已删除:{slug}")
    else:
        abort(404)
    return redirect(url_for("admin.dashboard"))


@bp.route("/sites", methods=["POST"])
@admin_required
def sites_add():
    name = request.form.get("name", "").strip()
    url = request.form.get("url", "").strip()
    description = request.form.get("description", "").strip()
    if not name or not url.startswith(("http://", "https://")):
        flash("名称必填,URL 需以 http(s):// 开头")
        return redirect(url_for("admin.dashboard"))
    sites = current_app.extensions["content"]["sites"]
    if any(s["url"] == url for s in sites):
        flash("该 URL 已存在")
        return redirect(url_for("admin.dashboard"))
    sites.append({"name": name, "url": url, "description": description})
    save_sites(_content_dir(), sites)
    _reload()
    flash(f"已添加:{name}")
    return redirect(url_for("admin.dashboard"))


@bp.route("/sites/delete", methods=["POST"])
@admin_required
def sites_delete():
    url = request.form.get("url", "")
    sites = current_app.extensions["content"]["sites"]
    remaining = [s for s in sites if s["url"] != url]
    if len(remaining) == len(sites):
        abort(404)
    save_sites(_content_dir(), remaining)
    _reload()
    flash("已删除站点")
    return redirect(url_for("admin.dashboard"))


def _post_form_from_request(slug=""):
    date_value = _parse_date(request.form.get("date", ""))
    return {
        "slug": slug or request.form.get("slug", "").strip().lower(),
        "title": request.form.get("title", "").strip(),
        "date": date_value or date.today(),
        "description": request.form.get("description", "").strip(),
        "draft": request.form.get("draft") == "on",
        "body": request.form.get("body", "").replace("\r\n", "\n"),
    }


def _validate_post_form(form, existing):
    if not form["title"]:
        return "标题不能为空"
    if not valid_slug(form["slug"]):
        return "slug 只能是小写字母、数字和连字符,如 my-first-post"
    if existing is None and load_post_raw(_content_dir(), form["slug"]) is not None:
        return "该 slug 已存在"
    return None
