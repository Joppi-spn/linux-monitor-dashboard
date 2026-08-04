from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import sqlite3
import os

app = FastAPI()

# 允许前端跨域请求（这样你在浏览器里直接打开 HTML 文件也能访问 API）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(os.path.dirname(__file__), 'monitor.db')

# ----- 接口1：获取最新一条数据 -----
@app.get("/api/latest")
def get_latest():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    sql = "SELECT timestamp, cpu_percent, mem_percent FROM metrics ORDER BY id DESC LIMIT 1"
    cursor.execute(sql)
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return {"error": "暂无数据"}
    return {
        "timestamp": row[0],
        "cpu": row[1],
        "memory": row[2]
    }

# ----- 接口2：获取历史数据（用于画图，默认返回最近30条） -----
@app.get("/api/history")
def get_history(limit: int = 30):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # 先取出最新的 N 条（倒序）
    cursor.execute(
        "SELECT timestamp, cpu_percent, mem_percent FROM metrics ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        return []
    # 反转顺序，让时间从旧到新（这样图表画出来是从左往右流动）
    rows.reverse()
    return [
        {"timestamp": r[0], "cpu": r[1], "memory": r[2]}
        for r in rows
    ]

# 挂载静态文件目录（用来放前端 HTML）
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
app.mount("/static", StaticFiles(directory=static_dir, html=True), name="static")
