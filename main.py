from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import sqlite3
import os
import re
import datetime
import hashlib
import json
import numpy as np
from sklearn.linear_model import LinearRegression

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(os.path.dirname(__file__), 'monitor.db')

# ==================== 区块链模块 ====================
class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data  # 存证内容（异常日志摘要）
        self.previous_hash = previous_hash
        self.hash = self.calc_hash()

    def calc_hash(self):
        # 将区块内容组合成字符串，计算 SHA256
        block_string = f"{self.index}{self.timestamp}{self.data}{self.previous_hash}"
        return hashlib.sha256(block_string.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = []
        # 创建创世区块（第一个区块）
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, datetime.datetime.now().isoformat(), "Genesis Block", "0")
        self.chain.append(genesis_block)

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, data):
        latest = self.get_latest_block()
        new_block = Block(
            index=latest.index + 1,
            timestamp=datetime.datetime.now().isoformat(),
            data=data,
            previous_hash=latest.hash
        )
        self.chain.append(new_block)
        return new_block

    def to_dict(self):
        return [
            {
                "index": block.index,
                "timestamp": block.timestamp,
                "data": block.data,
                "hash": block.hash,
                "previous_hash": block.previous_hash
            }
            for block in self.chain
        ]

# 初始化全局区块链实例（运行期间常驻内存）
blockchain = Blockchain()

# 记录已经存证过的日志内容（避免重复存证）
processed_logs = set()

def get_recent_error_logs(limit=10):
    """辅助函数：读取系统日志中的异常行"""
    log_path = "/var/log/syslog"
    if not os.path.exists(log_path):
        log_path = "/var/log/messages"
        if not os.path.exists(log_path):
            return []
    errors = []
    pattern = re.compile(r'(error|fail|out of memory|critical|panic)', re.IGNORECASE)
    try:
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        for line in reversed(lines):
            if pattern.search(line):
                clean = line.strip()
                if clean:
                    errors.append(clean)
                if len(errors) >= limit:
                    break
    except Exception:
        pass
    return errors

# ==================== 原有 API（不变） ====================
@app.get("/api/latest")
def get_latest():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, cpu_percent, mem_percent FROM metrics ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return {"error": "暂无数据"}
    return {"timestamp": row[0], "cpu": row[1], "memory": row[2]}

@app.get("/api/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.datetime.now().isoformat()}

@app.get("/api/metrics")
def get_metrics(hours: int = Query(24)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT timestamp, cpu_percent, mem_percent, disk_percent FROM metrics "
        "WHERE timestamp >= datetime('now', ?) ORDER BY id ASC",
        (f"-{hours} hours",)
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {"timestamp": r[0], "cpu": r[1], "memory": r[2], "disk": r[3]}
        for r in rows
    ]

@app.get("/api/logs")
def get_error_logs(limit: int = Query(100)):
    log_path = "/var/log/syslog"
    if not os.path.exists(log_path):
        log_path = "/var/log/messages"
        if not os.path.exists(log_path):
            return {"error": f"日志文件不存在", "logs": []}
    errors = []
    pattern = re.compile(r'(error|fail|out of memory|critical|panic)', re.IGNORECASE)
    try:
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        for line in reversed(lines):
            if pattern.search(line):
                clean_line = line.strip()[:500]
                errors.append(clean_line)
                if len(errors) >= limit:
                    break
    except Exception as e:
        return {"error": f"读取失败: {str(e)}", "logs": []}
    return {"total": len(errors), "logs": errors}

@app.get("/api/predict")
def predict_disk():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT timestamp, disk_percent FROM metrics "
        "WHERE timestamp >= datetime('now', '-2 hours') ORDER BY id ASC"
    )
    rows = cursor.fetchall()
    conn.close()
    if len(rows) < 10:
        return {"error": "数据不足（至少10个点）", "predicted_disk": None, "alert": False}
    X = np.array(range(len(rows))).reshape(-1, 1)
    y = np.array([r[1] for r in rows]).reshape(-1, 1)
    model = LinearRegression()
    model.fit(X, y)
    future_steps = 720
    future_X = np.array([[len(rows) + future_steps]])
    predicted = model.predict(future_X)[0][0]
    alert = bool(predicted > 85)
    return {
        "predicted_disk": round(predicted, 2),
        "alert": alert,
        "message": f"预计 1 小时后磁盘使用率 {round(predicted, 2)}%。",
        "sample_count": len(rows)
    }

# ==================== 新增：区块链 API ====================
@app.get("/api/blockchain/list")
def get_blockchain():
    """返回完整的区块链（所有存证记录）"""
    return {
        "chain": blockchain.to_dict(),
        "length": len(blockchain.chain)
    }

@app.post("/api/blockchain/mine")
def mine_block():
    """
    手动触发“挖矿”：扫描系统日志中的最新异常，生成新区块并上链。
    如果当前没有新异常，则返回提示。
    """
    global processed_logs
    # 获取最近的 10 条异常日志
    recent_errors = get_recent_error_logs(limit=10)
    
    if not recent_errors:
        return {"message": "当前系统日志中无异常记录", "block": None}
    
    # 找第一条尚未存证的日志
    new_log = None
    for log in recent_errors:
        if log not in processed_logs:
            new_log = log
            break
    
    if new_log is None:
        return {"message": "所有最近的异常日志均已存证，无新内容", "block": None}
    
    # 计算日志内容的哈希值（作为存证数据）
    log_hash = hashlib.sha256(new_log.encode()).hexdigest()
    # 构建议程数据（包含原始日志的哈希和部分原文，便于追溯）
    block_data = {
        "log_hash": log_hash,
        "log_preview": new_log[:100] + ("..." if len(new_log) > 100 else "")
    }
    
    # 添加到区块链
    new_block = blockchain.add_block(json.dumps(block_data))
    processed_logs.add(new_log)  # 标记为已处理
    
    return {
        "message": f"成功挖矿！已存证异常日志，区块索引 #{new_block.index}",
        "block": {
            "index": new_block.index,
            "timestamp": new_block.timestamp,
            "data": block_data,
            "hash": new_block.hash,
            "previous_hash": new_block.previous_hash
        }
    }

# ==================== 静态文件挂载 ====================
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
app.mount("/static", StaticFiles(directory=static_dir, html=True), name="static")
