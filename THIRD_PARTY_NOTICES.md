# 第三方组件与再分发说明

本仓只分发 Rongyi 整理后的项目源码和文档；依赖在构建或部署时由包管理器获取。使用、再分发或发布二进制前，请以各依赖的当前许可证和版本为准。

| 组件 | 用途 | 来源 / 许可入口 |
| :-- | :-- | :-- |
| Flask / Werkzeug | Python REST API | https://palletsprojects.com/p/flask/ · BSD-3-Clause |
| PyJWT | JWT 编解码 | https://github.com/jpadilla/pyjwt · MIT |
| PyMySQL | MySQL 客户端 | https://github.com/PyMySQL/PyMySQL · MIT |
| cryptography | PyMySQL 连接 MySQL 8 的 `caching_sha2_password` 认证支持 | https://github.com/pyca/cryptography · Apache-2.0 OR BSD-3-Clause |
| smbus2 | I²C 访问 | https://github.com/kplindegaard/smbus2 · MIT |
| Avalonia / Avalonia Desktop / Fluent | .NET 桌面界面 | https://avaloniaui.net/ · MIT |
| CommunityToolkit.Mvvm | MVVM 辅助 | https://github.com/CommunityToolkit/dotnet · MIT |
| ScottPlot.Avalonia | 历史图表 | https://scottplot.net/ · MIT |
| MySQL 8 Docker 镜像 | 可选本地联调数据库 | https://hub.docker.com/_/mysql · Oracle / MySQL 官方条款 |
| DHT22、BH1750 驱动 | 仅在真实 Raspberry Pi 上可选安装 | 由使用者按本机平台和上游许可证安装，不随本仓分发 |

仓库不分发树莓派系统镜像、MySQL 数据卷、真实数据库、账号、密码、Token、实物照片、视频、原理图、PCB、Gerber 或制造文件。
