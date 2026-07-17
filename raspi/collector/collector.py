"""
数据采集守护进程：周期性读传感器 -> 校验 -> 写入 MySQL -> 阈值判断 -> 写报警记录。

在 `raspi` 目录下运行:
    USE_MOCK_SENSORS=1 python -m collector.collector
"""
from __future__ import annotations

import logging
import time
from typing import Any, Dict, Optional

from collector import config
from collector.sensors import SensorReading, read_all
from db import connection, fetch_all

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("collector")


def _get_settings() -> Dict[str, str]:
    rows = fetch_all("SELECT setting_key, setting_value FROM settings")
    return {r["setting_key"]: str(r["setting_value"]) for r in rows}


def _float_setting(settings: Dict[str, str], key: str, default: float) -> float:
    try:
        return float(settings.get(key, default))
    except (TypeError, ValueError):
        return default


def _validate_reading(r: SensorReading) -> SensorReading:
    t, h, lux = r.temperature, r.humidity, r.light_lux
    if t is not None and not (-40 <= t <= 60):
        t = None
    if h is not None and not (0 <= h <= 100):
        h = None
    if lux is not None and lux < 0:
        lux = None
    return SensorReading(temperature=t, humidity=h, light_lux=lux)


def _check_alarms(
    cur,
    r: SensorReading,
    settings: Dict[str, str],
) -> None:
    th = _float_setting(settings, "temp_high", 40)
    tl = _float_setting(settings, "temp_low", 0)
    hh = _float_setting(settings, "humidity_high", 90)
    hl = _float_setting(settings, "humidity_low", 20)
    lh = _float_setting(settings, "light_high", 100000)
    ll = _float_setting(settings, "light_low", 0)

    checks: list[tuple[str, Optional[float], float, float]] = [
        ("temperature", r.temperature, tl, th),
        ("humidity", r.humidity, hl, hh),
        ("light_intensity", r.light_lux, ll, lh),
    ]
    for name, val, low, high in checks:
        if val is None:
            continue
        if val < low:
            cur.execute(
                """INSERT INTO alarms (param_name, param_value, threshold_value, alarm_type)
                   VALUES (%s, %s, %s, 'low')""",
                (name, val, low),
            )
        elif val > high:
            cur.execute(
                """INSERT INTO alarms (param_name, param_value, threshold_value, alarm_type)
                   VALUES (%s, %s, %s, 'high')""",
                (name, val, high),
            )


def run_loop() -> None:
    log.info(
        "Collector started (mock=%s, mysql=%s:%s/%s)",
        config.USE_MOCK_SENSORS,
        config.MYSQL_HOST,
        config.MYSQL_PORT,
        config.MYSQL_DATABASE,
    )
    while True:
        try:
            settings = _get_settings()
            interval = int(float(settings.get("collect_interval", "5")))
            interval = max(1, min(interval, 3600))
        except Exception as e:
            log.warning("settings load failed: %s, default interval=5", e)
            interval = 5
            settings = {}

        raw = read_all()
        r = _validate_reading(raw)
        try:
            with connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """INSERT INTO sensor_data (temperature, humidity, light_intensity)
                           VALUES (%s, %s, %s)""",
                        (r.temperature, r.humidity, r.light_lux),
                    )
                    if settings:
                        _check_alarms(cur, r, settings)
            log.info(
                "saved T=%s H=%s L=%s",
                r.temperature,
                r.humidity,
                r.light_lux,
            )
        except Exception as e:
            log.exception("DB write failed: %s", e)

        time.sleep(interval)


if __name__ == "__main__":
    run_loop()
