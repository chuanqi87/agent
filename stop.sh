#!/bin/bash

echo "🛑 停止AI Agent应用..."

# 检查是否在项目根目录
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ 请在项目根目录运行此脚本"
    exit 1
fi

# 停止服务函数
stop_services() {
    echo "🔍 查找并停止所有相关进程..."
    
    # 查找并终止后端进程
    echo "🔧 停止后端进程..."
    BACKEND_PIDS=$(ps aux | grep -E "(main\.py|uvicorn.*main:app)" | grep -v grep | awk '{print $2}')
    if [ ! -z "$BACKEND_PIDS" ]; then
        echo "⚠️ 发现后端进程: $BACKEND_PIDS"
        echo "$BACKEND_PIDS" | xargs kill -TERM 2>/dev/null
        sleep 2
        # 如果进程仍然存在，强制终止
        BACKEND_PIDS=$(ps aux | grep -E "(main\.py|uvicorn.*main:app)" | grep -v grep | awk '{print $2}')
        if [ ! -z "$BACKEND_PIDS" ]; then
            echo "🔥 强制终止后端进程..."
            echo "$BACKEND_PIDS" | xargs kill -9 2>/dev/null
        fi
        echo "✅ 后端进程已停止"
    else
        echo "✅ 没有发现后端进程"
    fi
    
    # 查找并终止前端进程
    echo "🎨 停止前端进程..."
    FRONTEND_PIDS=$(ps aux | grep -E "(npm.*run.*dev|vite)" | grep -v grep | awk '{print $2}')
    if [ ! -z "$FRONTEND_PIDS" ]; then
        echo "⚠️ 发现前端进程: $FRONTEND_PIDS"
        echo "$FRONTEND_PIDS" | xargs kill -TERM 2>/dev/null
        sleep 2
        # 如果进程仍然存在，强制终止
        FRONTEND_PIDS=$(ps aux | grep -E "(npm.*run.*dev|vite)" | grep -v grep | awk '{print $2}')
        if [ ! -z "$FRONTEND_PIDS" ]; then
            echo "🔥 强制终止前端进程..."
            echo "$FRONTEND_PIDS" | xargs kill -9 2>/dev/null
        fi
        echo "✅ 前端进程已停止"
    else
        echo "✅ 没有发现前端进程"
    fi
    
    # 清理端口占用
    echo "🧹 清理端口占用..."
    
    # 清理后端端口8000
    BACKEND_PORT_PID=$(lsof -ti:8000 2>/dev/null)
    if [ ! -z "$BACKEND_PORT_PID" ]; then
        echo "⚠️ 端口8000被占用 (PID: $BACKEND_PORT_PID)"
        kill -TERM $BACKEND_PORT_PID 2>/dev/null
        sleep 1
        kill -9 $BACKEND_PORT_PID 2>/dev/null
        echo "✅ 端口8000已释放"
    else
        echo "✅ 端口8000未被占用"
    fi
    
    # 清理前端端口5173
    FRONTEND_PORT_PID=$(lsof -ti:5173 2>/dev/null)
    if [ ! -z "$FRONTEND_PORT_PID" ]; then
        echo "⚠️ 端口5173被占用 (PID: $FRONTEND_PORT_PID)"
        kill -TERM $FRONTEND_PORT_PID 2>/dev/null
        sleep 1
        kill -9 $FRONTEND_PORT_PID 2>/dev/null
        echo "✅ 端口5173已释放"
    else
        echo "✅ 端口5173未被占用"
    fi
    
    echo "🎯 所有服务已停止"
}

# 执行停止操作
stop_services

echo ""
echo "✅ AI Agent应用已完全停止"
echo ""
echo "💡 提示:"
echo "   - 使用 './start.sh' 重新启动应用"
echo "   - 使用 './start.sh cleanup' 仅清理进程" 