from pathlib import Path

from werkzeug.security import check_password_hash, generate_password_hash


def _file(config):
    return Path(config["PASSWORD_FILE"])


def load_hash(config):
    f = _file(config)
    if f.exists():
        return f.read_text(encoding="utf-8").strip()
    return generate_password_hash(config["ADMIN_PASSWORD"])


def verify(config, password):
    return check_password_hash(load_hash(config), password)


def save(config, password):
    f = _file(config)
    f.write_text(generate_password_hash(password), encoding="utf-8")
