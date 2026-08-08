# Linux Monitor Dashboard - 系统资源监控看板
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
- **AI/ML**：Scikit-learn (线性回归)
- **系统监控**：Psutil
- **容器化**：Docker

### 前端
- **图表**：ECharts 5
- **交互**：原生 JavaScript + Fetch API
- **特色**：深色主题 + 响应式布局

### 安全与扩展
- **哈希算法**：SHA-256 (区块链存证)
- **跨域**：已配置 CORS 中间件

## ✨ 核心功能一览

- **📊 实时看板**：展示 CPU、内存、磁盘的实时使用率及历史趋势。
- **🤖 AI 磁盘预测**：基于过去 2 小时的数据，预测 1 小时后的磁盘占用率，并自动告警。
- **⚠️ 异常日志解析**：自动提取 `/var/log/syslog` 中的 `error/fail` 关键字。
- **⛓️ 区块链存证**：将异常日志的 SHA-256 哈希上链，形成不可篡改的存证记录。
- **📦 一键部署**：提供 Dockerfile，支持 `docker run` 快速启动。

## 🚀 快速开始

### 方式一：使用 Docker（推荐）

确保已安装 Docker，然后在终端执行：

```bash
# 拉取镜像（若已构建则跳过）
docker build -t linux-monitor:latest .

# 启动服务
docker run -d -p 8000:8000 --name monitor-app linux-monitor:latest

# 查看运行日志
docker logs -f monitor-app

### 方式二：在 Python 环境直接运行
bash
# 安装依赖
pip install -r requirements.txt

# 启动采集器（后台运行）
python3 collector.py &

# 启动 API 服务
uvicorn main:app --host 0.0.0.0 --port 8000
