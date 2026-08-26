from datetime import date

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from .content import load_site_content


def create_app(config_overrides=None):
    app = Flask(__name__)
    app.config.from_object("config.Config")
    if config_overrides:
        app.config.update(config_overrides)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    from .routes.main import bp as main_bp
    from .routes.webhook import bp as webhook_bp
    from .routes.admin import bp as admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(webhook_bp)
    app.register_blueprint(admin_bp)

    app.extensions["content"] = load_site_content(app.config["CONTENT_DIR"])

    @app.context_processor
    def _inject_globals():
        launch = app.config["SITE_LAUNCH_DATE"]
        return {
            "site_name": app.config["SITE_NAME"],
            "uptime_days": max((date.today() - launch).days, 0),
            "current_year": date.today().year,
        }

    return app
