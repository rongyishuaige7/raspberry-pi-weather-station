"""
Flask REST API：供 C# 上位机通过局域网 HTTP 调用。
在 `raspi` 目录:  FLASK_APP=api.app flask run --host=0.0.0.0 --port=5000
或: python -m api.app
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Optional

import decimal
import json
import logging

import jwt
from flask import Flask, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash


def _clean(obj: Any) -> Any:
    """递归把 Decimal 转成 float，把 datetime 转成字符串，让 jsonify 能序列化。"""
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: _clean(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_clean(i) for i in obj]
    return obj

import sys

# 保证从 raspi 目录运行时能导入 db
_RASPI_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RASPI_ROOT not in sys.path:
    sys.path.insert(0, _RASPI_ROOT)

from db import connection, fetch_all, fetch_one  # noqa: E402

JWT_SECRET = os.environ.get("JWT_SECRET", "").strip()
JWT_ALG = "HS256"
JWT_EXPIRE_HOURS = 72
log = logging.getLogger("weather_station.api")


def create_app() -> Flask:
    if len(JWT_SECRET) < 32:
        raise RuntimeError(
            "JWT_SECRET must be set to a deployment-specific value of at least "
            "32 characters. See raspi/.env.example."
        )
    app = Flask(__name__)

    def _token_from_request() -> Optional[str]:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            return auth[7:].strip()
        return None

    def _decode_token(token: str) -> Optional[dict]:
        try:
            return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        except jwt.PyJWTError:
            return None

    def require_auth(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = _token_from_request()
            if not token:
                return jsonify({"code": 401, "message": "未授权"}), 401
            payload = _decode_token(token)
            if not payload or "uid" not in payload:
                return jsonify({"code": 401, "message": "令牌无效"}), 401
            request.user_id = int(payload["uid"])  # type: ignore[attr-defined]
            request.user_role = payload.get("role", "user")  # type: ignore[attr-defined]
            return f(*args, **kwargs)

        return decorated

    @app.get("/api/health")
    def health():
        return jsonify({"code": 200, "message": "ok"})

    @app.post("/api/auth/register")
    def register():
        data = request.get_json(force=True, silent=True) or {}
        username = (data.get("username") or "").strip()
        password = data.get("password") or ""
        if len(username) < 2 or len(password) < 4:
            return jsonify({"code": 400, "message": "用户名或密码格式不正确"}), 400
        pw_hash = generate_password_hash(password)
        try:
            with connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, 'user')",
                        (username, pw_hash),
                    )
            return jsonify({"code": 200, "message": "注册成功"})
        except Exception as error:
            if "Duplicate" in str(error) or "1062" in str(error):
                return jsonify({"code": 409, "message": "用户名已存在"}), 409
            log.exception("registration failed")
            return jsonify({"code": 500, "message": "服务器内部错误"}), 500

    @app.post("/api/auth/login")
    def login():
        data = request.get_json(force=True, silent=True) or {}
        username = (data.get("username") or "").strip()
        password = data.get("password") or ""
        row = fetch_one(
            "SELECT id, username, password_hash, role FROM users WHERE username=%s",
            (username,),
        )
        if not row or not check_password_hash(row["password_hash"], password):
            return jsonify({"code": 401, "message": "用户名或密码错误"}), 401
        exp = datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS)
        token = jwt.encode(
            {"uid": row["id"], "role": row["role"], "exp": exp},
            JWT_SECRET,
            algorithm=JWT_ALG,
        )
        if isinstance(token, bytes):
            token = token.decode("utf-8")
        return jsonify(
            {
                "code": 200,
                "data": {
                    "token": token,
                    "username": row["username"],
                    "role": row["role"],
                },
            }
        )

    @app.post("/api/auth/password")
    @require_auth
    def change_password():
        data = request.get_json(force=True, silent=True) or {}
        old_p = data.get("old_password") or ""
        new_p = data.get("new_password") or ""
        if len(new_p) < 4:
            return jsonify({"code": 400, "message": "新密码过短"}), 400
        uid = request.user_id  # type: ignore[attr-defined]
        row = fetch_one("SELECT password_hash FROM users WHERE id=%s", (uid,))
        if not row or not check_password_hash(row["password_hash"], old_p):
            return jsonify({"code": 401, "message": "原密码错误"}), 401
        new_hash = generate_password_hash(new_p)
        with connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE users SET password_hash=%s WHERE id=%s", (new_hash, uid))
        return jsonify({"code": 200, "message": "密码已更新"})

    @app.get("/api/realtime")
    @require_auth
    def realtime():
        row = fetch_one(
            "SELECT id, temperature, humidity, light_intensity, recorded_at "
            "FROM sensor_data ORDER BY recorded_at DESC LIMIT 1"
        )
        if not row:
            return jsonify({"code": 200, "data": None})
        if row.get("recorded_at"):
            row["recorded_at"] = row["recorded_at"].isoformat(sep=" ")
        return jsonify({"code": 200, "data": _clean(row)})

    @app.get("/api/history")
    @require_auth
    def history():
        start = request.args.get("start")
        end = request.args.get("end")
        limit = min(int(request.args.get("limit", "500")), 5000)
        if not start or not end:
            return jsonify({"code": 400, "message": "需要 start 与 end 参数 (ISO 或 YYYY-MM-DD HH:MM:SS)"}), 400
        rows = fetch_all(
            "SELECT id, temperature, humidity, light_intensity, recorded_at "
            "FROM sensor_data WHERE recorded_at >= %s AND recorded_at <= %s "
            "ORDER BY recorded_at ASC LIMIT %s",
            (start, end, limit),
        )
        for r in rows:
            if r.get("recorded_at"):
                r["recorded_at"] = r["recorded_at"].isoformat(sep=" ")
        return jsonify({"code": 200, "data": _clean(rows)})

    @app.delete("/api/history/<int:record_id>")
    @require_auth
    def delete_history_record(record_id: int):
        with connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM sensor_data WHERE id=%s", (record_id,))
                affected = cur.rowcount
        if affected == 0:
            return jsonify({"code": 404, "message": "记录不存在"}), 404
        return jsonify({"code": 200, "message": "已删除"})

    @app.delete("/api/history")
    @require_auth
    def delete_all_history():
        start = request.args.get("start")
        end = request.args.get("end")
        with connection() as conn:
            with conn.cursor() as cur:
                if start and end:
                    cur.execute(
                        "DELETE FROM sensor_data WHERE recorded_at >= %s AND recorded_at <= %s",
                        (start, end),
                    )
                else:
                    cur.execute("DELETE FROM sensor_data")
                affected = cur.rowcount
        return jsonify({"code": 200, "message": f"已删除 {affected} 条记录", "data": {"deleted": affected}})

    @app.get("/api/alarms")
    @require_auth
    def alarms():
        limit = min(int(request.args.get("limit", "200")), 2000)
        rows = fetch_all(
            "SELECT id, param_name, param_value, threshold_value, alarm_type, "
            "triggered_at, acknowledged FROM alarms ORDER BY triggered_at DESC LIMIT %s",
            (limit,),
        )
        for r in rows:
            if r.get("triggered_at"):
                r["triggered_at"] = r["triggered_at"].isoformat(sep=" ")
        return jsonify({"code": 200, "data": _clean(rows)})

    @app.get("/api/settings")
    @require_auth
    def get_settings():
        rows = fetch_all("SELECT setting_key, setting_value, updated_at FROM settings")
        data = {r["setting_key"]: r["setting_value"] for r in rows}
        return jsonify({"code": 200, "data": data})

    @app.post("/api/settings")
    @require_auth
    def post_settings():
        body = request.get_json(force=True, silent=True) or {}
        if not isinstance(body, dict):
            return jsonify({"code": 400, "message": "无效 JSON"}), 400
        allowed = {
            "temp_high",
            "temp_low",
            "humidity_high",
            "humidity_low",
            "light_high",
            "light_low",
            "collect_interval",
        }
        updates: list[tuple[str, Any]] = []
        for k, v in body.items():
            if k in allowed and v is not None:
                updates.append((k, str(v)))
        if not updates:
            return jsonify({"code": 400, "message": "无可更新项"}), 400
        with connection() as conn:
            with conn.cursor() as cur:
                for k, v in updates:
                    cur.execute(
                        "INSERT INTO settings (setting_key, setting_value) VALUES (%s, %s) "
                        "ON DUPLICATE KEY UPDATE setting_value=%s",
                        (k, v, v),
                    )
        return jsonify({"code": 200, "message": "已保存"})

    @app.get("/api/devices")
    @require_auth
    def list_devices():
        rows = fetch_all(
            "SELECT id, device_name, device_no, location, status, created_at FROM devices ORDER BY id"
        )
        for r in rows:
            if r.get("created_at"):
                r["created_at"] = r["created_at"].isoformat(sep=" ")
        return jsonify({"code": 200, "data": rows})

    @app.post("/api/devices")
    @require_auth
    def add_device():
        data = request.get_json(force=True, silent=True) or {}
        name = (data.get("device_name") or "").strip()
        no = (data.get("device_no") or "").strip() or None
        loc = (data.get("location") or "").strip() or None
        if not name:
            return jsonify({"code": 400, "message": "device_name 必填"}), 400
        try:
            with connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO devices (device_name, device_no, location) VALUES (%s, %s, %s)",
                        (name, no, loc),
                    )
                    new_id = cur.lastrowid
            return jsonify({"code": 200, "data": {"id": new_id}})
        except Exception as error:
            if "Duplicate" in str(error) or "1062" in str(error):
                return jsonify({"code": 409, "message": "设备编号重复"}), 409
            log.exception("device creation failed")
            return jsonify({"code": 500, "message": "服务器内部错误"}), 500

    @app.put("/api/devices/<int:dev_id>")
    @require_auth
    def update_device(dev_id: int):
        data = request.get_json(force=True, silent=True) or {}
        fields = []
        args: list[Any] = []
        for col in ("device_name", "device_no", "location", "status"):
            if col in data and data[col] is not None:
                fields.append(f"{col}=%s")
                args.append(data[col])
        if not fields:
            return jsonify({"code": 400, "message": "无更新字段"}), 400
        args.append(dev_id)
        sql = f"UPDATE devices SET {', '.join(fields)} WHERE id=%s"
        with connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, tuple(args))
        return jsonify({"code": 200, "message": "已更新"})

    @app.delete("/api/devices/<int:dev_id>")
    @require_auth
    def delete_device(dev_id: int):
        with connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM devices WHERE id=%s", (dev_id,))
        return jsonify({"code": 200, "message": "已删除"})

    return app


app = create_app()


if __name__ == "__main__":
    host = os.environ.get("FLASK_HOST", "127.0.0.1")
    port = int(os.environ.get("FLASK_PORT", "5000"))
    app.run(host=host, port=port, debug=os.environ.get("FLASK_DEBUG") == "1")
