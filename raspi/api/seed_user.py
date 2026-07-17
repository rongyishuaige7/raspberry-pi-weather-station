"""创建默认管理员账户（可选）。"""
import os
import sys

_RASPI_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RASPI_ROOT not in sys.path:
    sys.path.insert(0, _RASPI_ROOT)

from werkzeug.security import generate_password_hash

from db import connection, fetch_one


def main() -> None:
    username = os.environ.get("ADMIN_USER", "").strip()
    password = os.environ.get("ADMIN_PASS", "")
    if len(username) < 2 or len(password) < 12:
        raise SystemExit(
            "Set ADMIN_USER (at least 2 characters) and ADMIN_PASS "
            "(at least 12 characters) before creating an administrator."
        )
    if fetch_one("SELECT id FROM users WHERE username=%s", (username,)):
        print(f"用户已存在: {username}")
        return
    h = generate_password_hash(password)
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, 'admin')",
                (username, h),
            )
    print(f"Administrator created for {username}. The password is not echoed.")


if __name__ == "__main__":
    main()
