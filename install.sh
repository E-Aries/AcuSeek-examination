#!/bin/bash
set -e

# =============================================
# AcuSeek 企业考核管理系统 - Linux 一键安装脚本
# 用法: chmod +x install.sh && sudo ./install.sh
# =============================================

PROJECT_DIR="/opt/AcuSeek"

echo "========================================"
echo " AcuSeek 企业考核管理系统 - 安装脚本"
echo "========================================"

# 1. 安装系统依赖
echo ""
echo "[1/6] 安装系统依赖..."
if command -v apt &> /dev/null; then
    apt update && apt install -y python3 python3-pip python3-venv nodejs npm git
elif command -v yum &> /dev/null; then
    yum install -y python3 python3-pip nodejs npm git
elif command -v dnf &> /dev/null; then
    dnf install -y python3 python3-pip nodejs npm git
else
    echo "请手动安装 python3、pip、nodejs、npm、git"
    exit 1
fi

# 2. 克隆项目
echo ""
echo "[2/6] 克隆项目..."
if [ -d "$PROJECT_DIR" ]; then
    echo "项目目录已存在，更新代码..."
    cd "$PROJECT_DIR"
    git pull
else
    git clone https://gitee.com/aries-minnasang/AcuSeek.git "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi

# 3. 安装后端依赖
echo ""
echo "[3/6] 安装后端依赖..."
cd "$PROJECT_DIR/backend"
pip3 install -r requirements.txt -q

# 4. 初始化数据库
echo ""
echo "[4/6] 初始化数据库..."
cd "$PROJECT_DIR"
python3 backend/seed.py

# 5. 安装前端依赖
echo ""
echo "[5/6] 安装前端依赖..."
npm install --no-audit --no-fund

# 6. 启动服务
echo ""
echo "[6/6] 启动服务..."
cd "$PROJECT_DIR/backend"
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /var/log/acuseek-backend.log 2>&1 &
BACKEND_PID=$!
echo "  后端已启动 (PID: $BACKEND_PID)"

cd "$PROJECT_DIR"
nohup npx vite --host --port 5173 > /var/log/acuseek-frontend.log 2>&1 &
FRONTEND_PID=$!
echo "  前端已启动 (PID: $FRONTEND_PID)"

sleep 3

# 验证
echo ""
echo "========================================"
echo " 安装完成!"
echo "========================================"
echo ""
echo " 前端地址:  http://$(curl -s ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}'):5173"
echo " 后端地址:  http://localhost:8000"
echo " API 文档:  http://localhost:8000/docs"
echo " 登录账号:  admin / admin123"
echo ""
echo " 日志文件:"
echo "   后端: tail -f /var/log/acuseek-backend.log"
echo "   前端: tail -f /var/log/acuseek-frontend.log"
echo ""
echo " MySQL 用户如需切换数据库:"
echo "   DATABASE_URL=\"mysql+pymysql://root:密码@localhost/acuseek\" python3 backend/seed.py"
echo ""
echo " 停止服务:"
echo "   pkill -f uvicorn && pkill -f vite"
echo ""