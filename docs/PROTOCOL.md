# API 与数据边界

树莓派端 Flask API 默认仅绑定回环地址；桌面端通过可配置的 HTTP Base URL 调用 API。HTTP、Bearer JWT 与本地 MySQL 只适合隔离可信教学网络，默认不具备 TLS、设备身份、细粒度授权、审计、速率限制、密钥轮换或公网暴露能力。

## 最小接口

| 方法 | 路径 | 鉴权 | 语义 |
| :-- | :-- | :-- | :-- |
| GET | `/api/health` | 否 | API 进程响应，不代表数据库、采集器或硬件健康 |
| POST | `/api/auth/register` | 否 | 创建普通用户 |
| POST | `/api/auth/login` | 否 | 换取短期 JWT |
| GET | `/api/realtime` | Bearer JWT | 返回数据库最近一条记录，不证明实时采样 |
| GET | `/api/history` | Bearer JWT | 查询时间范围内的存储记录 |
| GET/POST | `/api/settings` | Bearer JWT | 查询/修改软件阈值和采样间隔 |
| GET/POST/PUT/DELETE | `/api/devices` | Bearer JWT | 管理人工设备资料；`status` 不是在线证明 |

`USE_MOCK_SENSORS=1` 只应用于开发/CI。它产生的随机数不可当作真实数据，也不应上传到任何公开实例。
