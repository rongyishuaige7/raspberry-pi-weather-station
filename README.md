# 基于树莓派的多传感器小型气象站

> 面向嵌入式、局域网服务和桌面上位机学习的原型：树莓派采集 DHT22 温湿度与 BH1750 光照，写入 MySQL，经 Flask REST API 提供给 Avalonia / C# 上位机查看、查询历史和维护阈值。

[![Validate](https://github.com/rongyishuaige7/raspberry-pi-weather-station/actions/workflows/validate.yml/badge.svg)](https://github.com/rongyishuaige7/raspberry-pi-weather-station/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/Code-MIT-f97316.svg)](LICENSE)

> [!CAUTION]
> **使用提示：** 本项目用于嵌入式、局域网服务和桌面上位机学习；不是气象仪器、环境安全系统、消防报警系统、医疗设备或生产控制平台。

## 项目资料

这里整理了项目照片、界面截图和相关资料；文件处理说明见 [MEDIA_EVIDENCE](docs/MEDIA_EVIDENCE.md)。

![气象站界面，2026-04-07](assets/screenshots/historical-realtime-view.jpg)

## 系统范围

```text
DHT22 / BH1750
  → Raspberry Pi Python 采集器
  → MySQL：历史、阈值、报警、设备资料
  → Flask REST API（Bearer JWT）
  → Avalonia / C# 局域网桌面上位机
```

- **采集：** DHT22 温湿度、BH1750 光照；无硬件时可显式开启 mock。
- **服务：** Python、Flask、PyMySQL、MySQL；API 提供登录、实时记录、历史记录、阈值、报警和设备资料。
- **桌面端：** .NET 8、Avalonia、ScottPlot，适合学习本地上位机和 API 数据展示。
- **状态字段：** 数据库的 `devices.status` 由使用者维护；API `/api/health` 用于检查 API 服务可达性，桌面端显示最近一条数据库记录。

## 硬件与 BOM

| 模块/信号 | Raspberry Pi 接口 | 接线说明 |
| :-- | :-- | :-- |
| DHT22 DATA | GPIO4 / BCM 4 / 物理 Pin 7 | 3.3 V 逻辑；通常需 4.7 kΩ–10 kΩ 上拉，实物待确认 |
| BH1750 SDA / SCL | GPIO2 / GPIO3 / 物理 Pin 3 / 5 | I²C1；常见地址 `0x23` / `0x5C`，实物待确认 |
| DHT22 / BH1750 电源 | 3.3 V + GND | 模块电压、上拉、电平与公共地必须按实物复核 |

查看完整的 [BOM](hardware/BOM.csv)、[接线图](hardware/wiring-diagram.svg)和[硬件说明](HARDWARE.md)。不要把 5 V 信号直接接入 Raspberry Pi GPIO。

## 项目资料说明

`raspi/.env.example` 提供本地配置模板；真实 `raspi/.env` 被 Git 忽略。
## 本地构建与隔离联调

### 1. 准备配置

```bash
git clone https://github.com/rongyishuaige7/raspberry-pi-weather-station.git
cd raspberry-pi-weather-station
cp raspi/.env.example raspi/.env
# 编辑 raspi/.env，替换每个 replace_with_* 占位符
set -a && . raspi/.env && set +a
```

`raspi/.env` 包含部署凭据，必须保持本地、被 Git 忽略，不能上传、截图或写进日志。不要使用示例占位符作为真实口令。

### 2. 安装 Python 依赖

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r raspi/requirements.txt
```

DHT22 驱动根据实际 Raspberry Pi 型号和系统安装：较新内核通常使用 `adafruit-circuitpython-dht`，旧系统可评估 `Adafruit-DHT`。这些硬件驱动不随本仓分发。

### 3. 启动一次性本地 MySQL（可选）

在已加载 `raspi/.env` 的 shell 中：

```bash
docker compose up -d mysql
```

该 Compose 仅用于本机隔离联调，默认映射到 `127.0.0.1:13306`；同时在 `raspi/.env` 中设置 `MYSQL_PORT=13306`。它会创建含本地测试凭据的数据库端口映射；不要把它直接暴露到公网、共享网络或生产环境。停止并清理测试卷：

```bash
docker compose down -v
```

### 4. 无硬件 mock 联调

```bash
export USE_MOCK_SENSORS=1
export FLASK_HOST=127.0.0.1
export FLASK_PORT=5000

# 终端 1：在 raspi 目录运行采集器
(cd raspi && python3 -m collector.collector)

# 终端 2：在 raspi 目录运行 API
(cd raspi && python3 -m api.app)

# 终端 3：构建或运行桌面端
cd upper
dotnet restore WeatherStation.sln
dotnet run --project WeatherStation/WeatherStation.csproj
```

首次可在桌面端注册普通用户。若确实需要创建管理员，需显式设置强 `ADMIN_USER` 与至少 12 位的 `ADMIN_PASS`，然后在 `raspi/` 目录执行 `python3 -m api.seed_user`；命令不会回显口令。

服务默认绑定 `127.0.0.1`。需要在可信局域网联调时，才显式改为受控 LAN 地址，并自行处理防火墙、TLS、访问控制、密钥轮换与日志脱敏；本项目不提供公网部署方案。

### 5. 一键本地门禁

```bash
bash scripts/verify.sh
```

## API 与数据说明

| 方法 | 路径 | 鉴权 | 用途 |
| :-- | :-- | :-- | :-- |
| POST | `/api/auth/register` / `/api/auth/login` | 否 | 创建普通用户 / 换取 JWT |
| GET | `/api/history` | Bearer JWT | 查询已存记录 |
| GET/POST | `/api/settings` | Bearer JWT | 读取/修改软件阈值与采样间隔 |
| GET/POST/PUT/DELETE | `/api/devices` | Bearer JWT | 管理设备资料。 |

详见[协议说明](docs/PROTOCOL.md)。HTTP、Bearer JWT 和本地 MySQL 只适合隔离可信教学网络；没有 TLS、设备身份、细粒度权限、速率限制、审计或生产级密钥管理。

## 开源许可与第三方组件

项目源码以 [MIT License](LICENSE) 发布。Python、Avalonia、ScottPlot、MySQL 镜像和硬件驱动的来源与许可证边界见[第三方声明](THIRD_PARTY_NOTICES.md)。

## 安全

部署、凭据、网络暴露和状态表述限制见[SECURITY.md](SECURITY.md)。发现安全问题时，不要提交真实凭据或个人数据。
