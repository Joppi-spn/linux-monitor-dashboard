#!/usr/bin/env python3
"""
Linux 系统资源采集器
功能：采集 CPU、内存、磁盘、网络数据，存入 SQLite 数据库
"""

import psutil
import sqlite3
import time
import datetime
import os

# 数据库文件路径（与脚本同级）
DB_PATH = os.path.join(os.path.dirname(__file__), 'monitor.db')

def init_db():
    """初始化数据库，创建 metrics 表（如果不存在）"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            cpu_percent REAL,
            mem_total REAL,
            mem_available REAL,
            mem_percent REAL,
            disk_used REAL,
            disk_percent REAL,
            net_sent REAL,
            net_recv REAL
        )
    ''')
    conn.commit()
    conn.close()
    print(f"[系统] 数据库初始化完成: {DB_PATH}")

def collect_and_save():
    """执行一次数据采集并存入数据库"""
    try:
        # 1. 采集 CPU（间隔1秒取平均值，更准确）
        cpu = psutil.cpu_percent(interval=1)
        
        # 2. 采集内存（转换为 MB 单位，便于阅读）
        mem = psutil.virtual_memory()
        mem_total = mem.total / (1024 * 1024)
        mem_available = mem.available / (1024 * 1024)
        mem_percent = mem.percent
        
        # 3. 采集根目录磁盘（/）
        disk = psutil.disk_usage('/')
        disk_used = disk.used / (1024 * 1024)
        disk_percent = disk.percent
        
        # 4. 采集网络流量（累计字节数，换算为 MB）
        net = psutil.net_io_counters()
        net_sent = net.bytes_sent / (1024 * 1024)
        net_recv = net.bytes_recv / (1024 * 1024)
        
        # 5. 存入数据库
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO metrics 
            (cpu_percent, mem_total, mem_available, mem_percent, disk_used, disk_percent, net_sent, net_recv)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (cpu, mem_total, mem_available, mem_percent, disk_used, disk_percent, net_sent, net_recv))
        conn.commit()
        conn.close()
        
        # 6. 在终端打印一条简洁的日志（方便观察）
        now = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] CPU: {cpu}% | 内存: {mem_percent}% | 磁盘: {disk_percent}%")
        
    except Exception as e:
        print(f"[错误] 采集失败: {e}")

if __name__ == "__main__":
    print("=== Linux 监控采集器已启动 ===")
    init_db()
    print("开始循环采集 (按 Ctrl+C 停止)...\n")
    
    # 每隔 5 秒采集一次（你后续可以根据需求改为 3秒 或 10秒）
    interval = 5
    try:
        while True:
            collect_and_save()
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n[系统] 采集器已安全停止。")
