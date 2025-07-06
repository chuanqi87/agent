#!/bin/bash

# 清理历史进程的函数
cleanup_processes() {
    echo "🧹 清理历史进程..."
    
    # 查找并终止后端进程
    echo "🔍 查找后端进程..."
    BACKEND_PIDS=$(ps aux | grep -E "(main\.py|uvicorn.*main:app)" | grep -v grep | awk '{print $2}')
    if [ ! -z "$BACKEND_PIDS" ]; then
        echo "⚠️ 发现后端进程: $BACKEND_PIDS"
        echo "$BACKEND_PIDS" | xargs kill -9 2>/dev/null
        echo "✅ 后端进程已终止"
    else
        echo "✅ 没有发现后端进程"
    fi
    
    # 查找并终止前端进程
    echo "🔍 查找前端进程..."
    FRONTEND_PIDS=$(ps aux | grep -E "(npm.*run.*dev|vite)" | grep -v grep | awk '{print $2}')
    if [ ! -z "$FRONTEND_PIDS" ]; then
        echo "⚠️ 发现前端进程: $FRONTEND_PIDS"
        echo "$FRONTEND_PIDS" | xargs kill -9 2>/dev/null
        echo "✅ 前端进程已终止"
    else
        echo "✅ 没有发现前端进程"
    fi
    
    # 清理端口占用
    echo "🔍 检查端口占用..."
    
    # 检查后端端口8000
    BACKEND_PORT_PID=$(lsof -ti:8000 2>/dev/null)
    if [ ! -z "$BACKEND_PORT_PID" ]; then
        echo "⚠️ 端口8000被占用 (PID: $BACKEND_PORT_PID)"
        kill -9 $BACKEND_PORT_PID 2>/dev/null
        echo "✅ 端口8000已释放"
    else
        echo "✅ 端口8000未被占用"
    fi
    
    # 检查前端端口5173
    FRONTEND_PORT_PID=$(lsof -ti:5173 2>/dev/null)
    if [ ! -z "$FRONTEND_PORT_PID" ]; then
        echo "⚠️ 端口5173被占用 (PID: $FRONTEND_PORT_PID)"
        kill -9 $FRONTEND_PORT_PID 2>/dev/null
        echo "✅ 端口5173已释放"
    else
        echo "✅ 端口5173未被占用"
    fi
    
    echo "🎯 进程清理完成"
    echo ""
}

# 检查命令行参数
if [ "$1" = "cleanup" ] || [ "$1" = "clean" ]; then
    echo "🧹 仅执行清理操作..."
    # 检查是否在项目根目录
    if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
        echo "❌ 请在项目根目录运行此脚本"
        exit 1
    fi
    # 执行清理函数
    cleanup_processes
    echo "✅ 清理完成，退出"
    exit 0
fi

echo "🚀 启动AI Agent应用..."

# 检查是否在项目根目录
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ 请在项目根目录运行此脚本"
    exit 1
fi

# 执行清理
cleanup_processes

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

# 优雅关闭函数
graceful_shutdown() {
    echo ""
    echo "🛑 正在停止服务..."
    
    # 终止后端进程
    if [ ! -z "$BACKEND_PID" ]; then
        echo "🔧 停止后端服务 (PID: $BACKEND_PID)..."
        kill -TERM $BACKEND_PID 2>/dev/null
        sleep 2
        kill -9 $BACKEND_PID 2>/dev/null
    fi
    
    # 终止前端进程
    if [ ! -z "$FRONTEND_PID" ]; then
        echo "🎨 停止前端服务 (PID: $FRONTEND_PID)..."
        kill -TERM $FRONTEND_PID 2>/dev/null
        sleep 2
        kill -9 $FRONTEND_PID 2>/dev/null
    fi
    
    # 再次清理端口（确保完全释放）
    echo "🧹 最终清理端口..."
    lsof -ti:8000 2>/dev/null | xargs kill -9 2>/dev/null
    lsof -ti:5173 2>/dev/null | xargs kill -9 2>/dev/null
    
    echo "✅ 所有服务已停止"
    exit 0
}

# 等待用户中断
trap graceful_shutdown INT TERM
wait 