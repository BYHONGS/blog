import hashlib
import hmac
import subprocess
import threading

from flask import Blueprint, abort, current_app, request

bp = Blueprint("webhook", __name__)


@bp.post("/api/webhook")
def github_webhook():
    secret = current_app.config["WEBHOOK_SECRET"]
    signature = request.headers.get("X-Hub-Signature-256", "")
    expected = (
        "sha256="
        + hmac.new(secret.encode(), request.get_data(), hashlib.sha256).hexdigest()
    )
    if not secret or not hmac.compare_digest(expected, signature):
        abort(403)

    payload = request.get_json(silent=True) or {}
    ref = payload.get("ref")
    if ref is None:
        return {"ok": True}
    if ref != "refs/heads/master":
        return {"ok": True, "ignored": ref}

    repo_dir = current_app.config["REPO_DIR"]
    run_deploy = current_app.config["RUN_DEPLOY"]
    threading.Thread(target=_deploy, args=(repo_dir, run_deploy), daemon=True).start()
    return {"ok": True, "deploying": True}, 202


def _deploy(repo_dir, run_deploy):
    subprocess.run(
        ["git", "-C", str(repo_dir), "pull", "--ff-only"],
        check=False,
        capture_output=True,
    )
    if run_deploy:
        subprocess.run(
            ["sudo", "-n", "systemctl", "restart", "blog"],
            check=False,
            capture_output=True,
        )
