from flask import Blueprint, Response, abort, current_app, render_template, request, url_for

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["POSTS_PER_PAGE"]
    posts = current_app.extensions["content"]["posts"]
    total_pages = max((len(posts) + per_page - 1) // per_page, 1)
    if page < 1 or page > total_pages:
        abort(404)
    start = (page - 1) * per_page
    return render_template(
        "index.html",
        posts=posts[start : start + per_page],
        page=page,
        total_pages=total_pages,
    )


@bp.route("/posts/<slug>/")
def post(slug):
    for post in current_app.extensions["content"]["posts"]:
        if post.slug == slug:
            return render_template("post.html", post=post)
    abort(404)


@bp.route("/about/")
def about():
    about_html = current_app.extensions["content"]["about_html"]
    if not about_html:
        abort(404)
    return render_template("about.html", about_html=about_html)


@bp.route("/sites/")
def sites():
    return render_template(
        "sites.html", sites=current_app.extensions["content"]["sites"]
    )


@bp.route("/sitemap.xml")
def sitemap():
    posts = current_app.extensions["content"]["posts"]
    xml = render_template("sitemap.xml", posts=posts)
    return Response(xml, mimetype="application/xml")


@bp.route("/robots.txt")
def robots():
    body = (
        "User-agent: *\n"
        "Allow: /\n"
        f"Sitemap: {url_for('main.sitemap', _external=True)}\n"
    )
    return Response(body, mimetype="text/plain")
