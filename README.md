# 🐧 Linux 智能监控系统 · 区块链存证版

[![Docker Pulls](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://hub.docker.com)
[![Python 3.10](https://img.shields.io/badge/Python-3.10-green?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-teal?logo=fastapi)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📌 项目简介

这是一个面向 Linux 服务器的轻量级监控平台，集成了 **实时数据采集**、**AI 趋势预测** 和 **区块链防篡改存证** 三大核心功能。项目采用 **前后端分离** 架构，所有组件均已 **Docker 容器化**，可一键部署运行。

**适用场景**：个人服务器运维、技术项目展示、云计算课程实验、中小型公司内部监控。

## 🛠 技术栈

### 后端
- **语言**：Python 3.10
- **框架**：FastAPI + Uvicorn
- **数据库**：SQLite
- **AI/ML**：Scikit‑learn (线性回归)
- **系统监控**：Psutil
- **容器化**：Docker

### 前端
- **图表**：ECharts 5
- **交互**：原生 JavaScript + Fetch API
- **特色**：深色主题 + 响应式布局

### 安全与扩展
- **哈希算法**：SHA‑256 (区块链存证)
- **跨域**：已配置 CORS 中间件

## ✨ 核心功能一览

- **📊 实时看板**：展示 CPU、内存、磁盘的实时使用率及历史趋势。
- **🤖 AI 磁盘预测**：基于过去 2 小时的数据，预测 1 小时后的磁盘占用率，并自动告警。
- **⚠️ 异常日志解析**：自动提取 `/var/log/syslog` 中的 `error/fail` 关键字。
- **⛓️ 区块链存证**：将异常日志的 SHA‑256 哈希上链，形成不可篡改的存证记录。
- **📦 一键部署**：提供 Dockerfile，支持 `docker run` 快速启动。

## 🚀 快速开始

### 方式一：使用 Docker（推荐）

确保已安装 Docker，然后在终端执行：

```bash
# 构建镜像
docker build -t linux-monitor:latest .

# 启动服务
docker run -d -p 8000:8000 --name monitor-app linux-monitor:latest

# 查看运行日志
docker logs -f monitor-app
```

启动后访问：
```
http://你的服务器IP:8000/static/index.html
```

### 方式二：Python 环境直接运行

```bash
# 安装依赖
pip install -r requirements.txt

# 启动采集器（后台运行）
python3 collector.py &

# 启动 API 服务
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📸 项目截图

> 将截图命名为 `screenshot.png`，放置项目根目录。

![项目看板截图](./screenshot.png)

> 图：深色主题看板，展示 CPU、内存、磁盘曲线，以及 AI 预测卡片和区块链列表。

## 🧪 API 接口文档

启动服务后，访问交互式 Swagger 文档：
```
http://你的服务器IP:8000/docs
```

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/latest` | GET | 获取最新一条监控数据 |
| `/api/metrics` | GET | 获取指定小时数的历史趋势 |
| `/api/predict` | GET | AI 预测未来磁盘占用率 |
| `/api/logs` | GET | 获取系统异常日志 |
| `/api/blockchain/list` | GET | 查看所有已存证区块 |
| `/api/blockchain/mine` | POST | 手动触发“挖矿”存证异常日志 |

## 🧠 项目亮点与挑战

- **AI 预测落地**：使用最简单的线性回归，实现了“未来趋势”的可视化，而非单纯展示过去。
- **区块链防篡改**：每个新区块包含前一个区块的哈希，形成完整的验证链条。
- **全容器化交付**：通过 Docker 屏蔽环境差异，真正做到“一次构建，处处运行”。
- **前后端联调**：独立完成从接口设计到前端定时刷新的全链路闭环。

## 📂 项目结构

```text
.
├── collector.py          # 数据采集器（每5秒抓取系统状态）
├── main.py               # FastAPI 主程序（含所有接口及区块链逻辑）
├── requirements.txt      # Python 依赖清单
├── start.sh              # 容器启动脚本（同时拉起采集器与 API）
├── Dockerfile            # 容器构建文件
├── .dockerignore         # 构建忽略文件
├── static/
│   └── index.html        # 前端可视化看板（ECharts + 原生JS）
├── tests/
│   └── test_main.py      # 单元测试（pytest）
└── README.md             # 项目文档
```

## 🔮 未来优化方向

- [ ] 支持多服务器同时监控（增加 host 字段）
- [ ] 增加告警通知（邮件 / 钉钉机器人）
- [ ] 将 SQLite 升级为 PostgreSQL，支持高并发
- [ ] 自动挖矿：后台线程定时扫描日志并自动上链

## 🤝 贡献与反馈

欢迎通过 Issue 或 Pull Request 提出建议！
如果你觉得这个项目对你有帮助，欢迎 Star ⭐️ 支持一下。
