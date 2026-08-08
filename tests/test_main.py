import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    """测试健康检查接口是否返回 200"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data

def test_latest_api():
    """测试最新数据接口是否返回有效结构"""
    response = client.get("/api/latest")
    assert response.status_code == 200
    data = response.json()
    # 如果有数据，应该包含 timestamp, cpu, memory；如果没数据，包含 error
    if "error" not in data:
        assert "timestamp" in data
        assert "cpu" in data
        assert "memory" in data

def test_metrics_api():
    """测试历史数据接口返回的是列表"""
    response = client.get("/api/metrics?hours=1")
    assert response.status_code == 200
    data = response.json()
    # 无论有没有数据，都应该是列表格式
    assert isinstance(data, list)
