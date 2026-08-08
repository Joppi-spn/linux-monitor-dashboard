#!/bin/bash
# 启动采集器（后台运行）
python3 collector.py &
# 启动 API（前台运行，保持容器活跃）
uvicorn main:app --host 0.0.0.0 --port 8000
