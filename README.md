# 基于树莓派的多传感器小型气象站

> 面向嵌入式、局域网服务和桌面上位机学习的原型：树莓派采集 DHT22 温湿度与 BH1750 光照，写入 MySQL，经 Flask REST API 提供给 Avalonia / C# 上位机查看、查询历史和维护阈值。

[![Validate](https://github.com/rongyishuaige7/raspberry-pi-weather-station/actions/workflows/validate.yml/badge.svg)](https://github.com/rongyishuaige7/raspberry-pi-weather-station/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/Code-MIT-f97316.svg)](LICENSE)
[![Hardware retest](https://img.shields.io/badge/hardware-not%20retested-6e7781.svg)](docs/PROJECT_STATUS.md)

> [!CAUTION]
> 这是本科软硬件学习原型，不是气象仪器、环境安全系统、消防/报警系统、医疗设备、生产控制或远程运维平台。传感器读数、阈值、模拟数据、API 响应和桌面界面都不能代替经过标定的测量、告警送达、设备在线证明或安全结论。

## 当前证据

```text
源码来源已确认
公开候选不含部署凭据、数据库卷、IDE 状态或发布二进制
本机公开门禁、Python 源码契约、.NET/Avalonia 桌面端构建与隔离 MySQL mock 联调已验证；GitHub Actions 工作流已配置。默认分支的实时构建结果以仓库徽章和 [Hardware Lab 索引](https://github.com/rongyishuaige7/hardware-lab)中按当前 HEAD 核验的固定证据为准
当前 Raspberry Pi、DHT22、BH1750、真实 MySQL 部署与 LAN 端到端链路尚未按当前公开 commit 重新真机复测
```

CI 中的 `USE_MOCK_SENSORS=1` 生成随机模拟数据，仅用于隔离开发验证；它不代表真实传感器、当前天气、设备在线或环境状态。完整范围见[项目状态](docs/PROJECT_STATUS.md)和[验证说明](docs/VERIFICATION.md)。

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
- **状态语义：** 数据库中的 `devices.status` 是人工维护字段；API `/api/health` 只说明 API 进程响应；桌面“已收到最近一条记录”只说明查询到了数据库最近记录，均不是设备在线、采集器运行或传感器真实工作的证明。

## 硬件与 BOM

| 模块/信号 | Raspberry Pi 接口 | 当前源码边界 |
| :-- | :-- | :-- |
| DHT22 DATA | GPIO4 / BCM 4 / 物理 Pin 7 | 3.3 V 逻辑；通常需 4.7 kΩ–10 kΩ 上拉，实物待确认 |
| BH1750 SDA / SCL | GPIO2 / GPIO3 / 物理 Pin 3 / 5 | I²C1；常见地址 `0x23` / `0x5C`，实物待确认 |
| DHT22 / BH1750 电源 | 3.3 V + GND | 模块电压、上拉、电平与公共地必须按实物复核 |

查看完整的 [BOM](hardware/BOM.csv)、[源码推导接线边界图](hardware/wiring-diagram.svg) 和[硬件说明](HARDWARE.md)。该图不是原理图、PCB 或已完成真机复测的接线证明。不要把 5 V 信号直接接入 Raspberry Pi GPIO。

## 公开净化与来源

- 权威源码来自桌面原工程；历史 ZIP 与公开整理前的有效源码逐字节一致。
- 原工程和 ZIP 保持只读，净化、文档和提交只在本公开候选中发生。
- 公开仓不包含真实数据库、用户、密码、JWT、私网地址、部署配置、系统镜像、实物照片、视频、EDA、PCB、Gerber 或制造文件。
- 已移除 IDE 状态和默认图标；`raspi/.env.example` 只提供不可用占位符，真实 `raspi/.env` 被 Git 忽略。

详情见[来源与公开范围](docs/SOURCE_PROVENANCE.md)。

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

该脚本运行公开边界检查、Python 语法/源码契约测试和 Avalonia Release 构建。它不启动 Docker、不写入真实数据库、不烧录树莓派，也不代替 GitHub Actions 的隔离 MySQL mock 联调。

## API 与数据边界

| 方法 | 路径 | 鉴权 | 真实语义 |
| :-- | :-- | :-- | :-- |
| GET | `/api/health` | 否 | API 进程响应，不代表数据库、采集器或硬件健康 |
| POST | `/api/auth/register` / `/api/auth/login` | 否 | 创建普通用户 / 换取 JWT |
| GET | `/api/realtime` | Bearer JWT | 数据库最近一条记录，不代表实时采样 |
| GET | `/api/history` | Bearer JWT | 查询已存记录 |
| GET/POST | `/api/settings` | Bearer JWT | 读取/修改软件阈值与采样间隔 |
| GET/POST/PUT/DELETE | `/api/devices` | Bearer JWT | 管理人工设备资料；状态字段不是在线证明 |

详见[协议说明](docs/PROTOCOL.md)。HTTP、Bearer JWT 和本地 MySQL 只适合隔离可信教学网络；没有 TLS、设备身份、细粒度权限、速率限制、审计或生产级密钥管理。

## 验证与真机复测

当前 CI 验证的是公开文件边界、Python/API 契约、隔离 MySQL、mock 数据链路和 .NET/Avalonia 构建。它不验证真实 Raspberry Pi、DHT22、BH1750、I²C、GPIO、真实 LAN、长期运行、数据准确性或预警效果。

要升级为当前真机已复测，必须按[真机复测清单](docs/VERIFICATION.md)记录日期、精确 Git commit、硬件型号、供电、接线、I²C 地址、每项通过/失败结果和脱敏运行证据。

## 开源许可与第三方组件

项目源码以 [MIT License](LICENSE) 发布。Python、Avalonia、ScottPlot、MySQL 镜像和硬件驱动的来源与许可证边界见[第三方声明](THIRD_PARTY_NOTICES.md)。

## 安全

部署、凭据、网络暴露和状态表述限制见[SECURITY.md](SECURITY.md)。发现安全问题时，不要提交真实凭据或个人数据。
