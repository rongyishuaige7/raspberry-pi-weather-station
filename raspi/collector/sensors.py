"""温湿度与光照传感器读取；无硬件时使用模拟数据。"""
from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Optional, Tuple

from . import config


@dataclass
class SensorReading:
    temperature: Optional[float]
    humidity: Optional[float]
    light_lux: Optional[float]


def _mock_reading() -> SensorReading:
    base_t = 22.0 + random.uniform(-2, 2)
    base_h = 55.0 + random.uniform(-5, 5)
    base_l = 300.0 + random.uniform(-30, 30)
    return SensorReading(
        temperature=round(base_t, 2),
        humidity=round(base_h, 2),
        light_lux=round(base_l, 2),
    )


def read_dht22() -> Tuple[Optional[float], Optional[float]]:
    """返回 (温度℃, 相对湿度%)。失败返回 (None, None)。

    优先使用 adafruit-circuitpython-dht（支持树莓派 5 新内核），
    回退使用旧版 Adafruit_DHT。
    """
    if config.USE_MOCK_SENSORS:
        m = _mock_reading()
        return m.temperature, m.humidity

    # 方式 A：新版 circuitpython-dht（树莓派 5 推荐）
    try:
        import board
        import adafruit_dht

        pin = getattr(board, f"D{config.DHT_PIN}", None)
        if pin is None:
            raise ImportError(f"board.D{config.DHT_PIN} not found")
        dht = adafruit_dht.DHT22(pin, use_pulseio=False)
        for _ in range(5):
            try:
                t = dht.temperature
                h = dht.humidity
                if t is not None and h is not None:
                    dht.exit()
                    return round(float(t), 2), round(float(h), 2)
            except RuntimeError:
                time.sleep(2)
        dht.exit()
        return None, None
    except ImportError:
        pass
    except Exception:
        pass

    # 方式 B：旧版 Adafruit_DHT（树莓派 4 及更早）
    try:
        import Adafruit_DHT

        h, t = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, config.DHT_PIN, retries=3, delay_seconds=2)
        if t is not None and h is not None:
            return round(float(t), 2), round(float(h), 2)
    except Exception:
        pass

    return None, None


def read_bh1750() -> Optional[float]:
    """返回光照强度 lux；失败返回 None。"""
    if config.USE_MOCK_SENSORS:
        return _mock_reading().light_lux

    try:
        from smbus2 import SMBus

        bus = SMBus(config.I2C_BUS)
        addr = config.BH1750_ADDR
        bus.write_byte(addr, 0x10)
        time.sleep(0.18)
        data = bus.read_i2c_block_data(addr, 0x00, 2)
        bus.close()
        lux = (data[0] << 8 | data[1]) / 1.2
        return round(float(lux), 2)
    except Exception:
        return None


def read_all() -> SensorReading:
    t, h = read_dht22()
    lux = read_bh1750()
    return SensorReading(temperature=t, humidity=h, light_lux=lux)
