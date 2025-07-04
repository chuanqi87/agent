#!/bin/bash

echo "🚀 启动AI Agent应用..."

# 检查是否在项目根目录
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ 请在项目根目录运行此脚本"
    exit 1
fi

# 启动后端
echo "📡 启动后端服务..."
cd backend
if [ ! -f ".env" ]; then
    echo "⚠️ 未找到.env文件，请复制.env.example并配置API密钥"
    cp .env.example .env 2>/dev/null || true
fi

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "🔧 创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境并安装依赖
source venv/bin/activate
pip install -r requirements.txt

# 在后台启动后端
echo "🌟 启动后端服务 (后台运行)..."
python main.py &
BACKEND_PID=$!

cd ..

# 启动前端
echo "🎨 启动前端服务..."
cd frontend

# 安装前端依赖
if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install
fi

# 启动前端开发服务器
echo "🌐 启动前端开发服务器..."
npm run dev &
FRONTEND_PID=$!

# 显示服务信息
echo ""
echo "🎉 应用启动完成！"
echo "📱 前端地址: http://localhost:5173"
echo "🔧 后端地址: http://localhost:8000"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待用户中断
trap "echo '🛑 正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait 