"""采集服务与 API 共用的环境配置。

本模块不保存数据库口令、JWT 密钥或其他部署凭据。部署前请从
``raspi/.env.example`` 创建一个仅保存在本机、被 Git 忽略的 ``raspi/.env``，
并由 shell 或服务管理器显式加载。
"""
import os


def _required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(
            f"{name} is required. Copy raspi/.env.example to raspi/.env and "
            "provide a deployment-specific value."
        )
    return value


# MySQL connection facts; credentials are deliberately required rather than
# falling back to a sample password.
MYSQL_HOST = os.environ.get("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT", "3306"))
MYSQL_USER = _required("MYSQL_USER")
MYSQL_PASSWORD = _required("MYSQL_PASSWORD")
MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "weather_station")

# 传感器：在 PC 调试或无硬件时设为 1
USE_MOCK_SENSORS = os.environ.get("USE_MOCK_SENSORS", "0") == "1"

# DHT22 DATA 引脚（BCM 编号）
DHT_PIN = int(os.environ.get("DHT_PIN", "4"))

# BH1750 I2C 地址（常见 0x23 或 0x5C）
BH1750_ADDR = int(os.environ.get("BH1750_ADDR", "0x23"), 16)

# I2C 总线编号（树莓派一般为 1）
I2C_BUS = int(os.environ.get("I2C_BUS", "1"))
