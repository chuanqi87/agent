# AI Agent 聊天应用

一个基于Vue前端和LangChain + DeepSeek后端的AI Agent聊天应用。

## 项目结构

```
uni-agent/
├── frontend/          # Vue前端应用
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...
├── backend/           # LangChain后端应用
│   ├── app/
│   ├── requirements.txt
│   └── main.py
└── README.md
```

## 快速开始

### 🚀 一键启动（推荐）

```bash
./start.sh
```

服务启动后：
- 前端地址: http://localhost:5173
- 后端地址: http://localhost:8000

### 🛑 停止服务

```bash
# 方式1：使用专用停止脚本
./stop.sh

# 方式2：仅清理历史进程（不启动服务）
./start.sh cleanup
# 或者
./start.sh clean

# 方式3：在运行中的服务中按 Ctrl+C
```

### 🧹 脚本功能

- **`./start.sh`** - 启动应用（会自动清理历史进程）
- **`./start.sh cleanup`** - 仅清理历史进程，不启动服务
- **`./stop.sh`** - 优雅停止所有服务

### 手动启动（开发调试）

#### 后端启动

```bash
cd backend
pip install -r requirements.txt
python main.py
```

#### 前端启动

```bash
cd frontend
npm install
npm run dev
```

## 功能特性

- 🌟 Vue 3 + Composition API
- 🚀 LangChain 集成
- 💬 实时聊天界面
- 🤖 AI Agent 对话
- 📡 WebSocket 实时通信

## 技术栈

### 前端
- Vue 3
- TypeScript
- Tailwind CSS
- Socket.io-client

### 后端
- FastAPI
- LangChain + DeepSeek V3
- Socket.io
- Python 3.8+ 