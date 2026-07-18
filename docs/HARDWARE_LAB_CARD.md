# Hardware Lab 索引卡片

- **名称：** 基于树莓派的多传感器小型气象站
- **平台：** Raspberry Pi · Python · Flask · MySQL · C# · Avalonia · DHT22 · BH1750
- **摘要：** 树莓派端采集 DHT22 与 BH1750，写入 MySQL 并通过 Flask REST API 提供实时、历史、阈值、报警和设备资料；Avalonia 上位机完成局域网管理展示。
- **构建证据：** 以 [Hardware Lab 当前索引](https://github.com/rongyishuaige7/hardware-lab)为准；该索引会核对固定成功 Actions 运行与远程默认分支 HEAD 一致。本文件不声称自身所在 commit 已完成 CI。
- **真机状态：** 源码来源、公开净化、Python/API/数据库 mock 联调与桌面构建可验证；当前 Raspberry Pi、DHT22、BH1750、真实 MySQL 部署与 LAN 端到端链路尚未按当前公开提交重新真机复测。
- **公开范围：** 当前未公开实物照片、演示视频、EDA、PCB、Gerber、制造文件、系统镜像或真实数据库；已公开源码、BOM、接线边界、协议、来源和验证说明。
- **关键边界：** mock 不代表真实传感器；HTTP/JWT/MySQL 只限可信局域网；设备状态字段不是在线状态；不能用于气象、环境安全或生产控制结论。

- **项目素材：** 已补充项目照片、界面截图和相关资料；范围和版本差异见 [`MEDIA_EVIDENCE.md`](MEDIA_EVIDENCE.md)。
