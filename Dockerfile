FROM python:3.10-slim

WORKDIR /app

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制项目所有文件
COPY . .

# 给启动脚本权限
RUN chmod +x start.sh

# 暴露端口
EXPOSE 8000

# 容器启动时执行启动脚本
CMD ["./start.sh"]
