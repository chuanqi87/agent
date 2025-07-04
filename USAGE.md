# AI Agent 聊天应用使用指南

## 快速启动

### 1. 环境准备

确保您的系统已安装：
- Python 3.8+
- Node.js 16+
- npm 或 yarn

### 2. API 配置

项目已预配置使用 **DeepSeek API**：

- **模型**: deepseek-chat (DeepSeek-V3)
- **API Base URL**: https://api.deepseek.com/v1
- **API 密钥**: 已预设

如需修改配置：
```bash
cd backend
# 编辑 .env 文件
nano .env
```

`.env` 文件内容：
```env
# DeepSeek API配置
OPENAI_API_KEY=sk-2dbab3ae60f145e8839bb8781de06071
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-chat
```

### 3. 一键启动

使用提供的启动脚本：

```bash
chmod +x start.sh
./start.sh
```

### 4. 手动启动（可选）

如果一键启动脚本不工作，可以手动启动：

#### 启动后端
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

#### 启动前端
```bash
cd frontend
npm install
npm run dev
```

## 访问应用

- 前端界面: http://localhost:5173
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 功能特性

### 聊天功能
- 实时对话界面
- WebSocket 实时通信
- 消息历史记录
- 思考状态显示

### 技术特性
- Vue 3 + TypeScript
- Tailwind CSS 响应式设计
- Pinia 状态管理
- Socket.IO 实时通信
- LangChain + DeepSeek V3 AI 集成
- FastAPI 后端服务

## 故障排除

### 常见问题

1. **连接失败**
   - 检查后端服务是否正常运行
   - 确认端口 8000 和 5173 未被占用

2. **API 密钥错误**
   - 检查 `.env` 文件中的 `OPENAI_API_KEY`
   - 确保 DeepSeek API 密钥有效且有余额

3. **依赖安装失败**
   - 更新 pip: `pip install --upgrade pip`
   - 更新 npm: `npm install -g npm@latest`

### 开发模式

#### 后端开发
```bash
cd backend
source venv/bin/activate
uvicorn app.server:app --reload --host 0.0.0.0 --port 8000
```

#### 前端开发
```bash
cd frontend
npm run dev
```

## 自定义配置

### 修改 AI 模型
编辑 `backend/.env`，可选择以下DeepSeek模型：
```env
# 主要聊天模型（推荐）
OPENAI_MODEL=deepseek-chat

# 推理模型（适合复杂逻辑推理）
OPENAI_MODEL=deepseek-reasoner
```

### 修改端口
- 后端端口: 修改 `backend/.env` 中的 `APP_PORT`
- 前端端口: 修改 `frontend/vite.config.ts` 中的 `server.port`

## 项目结构

```
uni-agent/
├── frontend/              # Vue 前端应用
│   ├── src/
│   │   ├── components/    # 组件目录（可扩展）
│   │   ├── views/         # 页面组件
│   │   ├── stores/        # Pinia 状态管理
│   │   ├── router/        # 路由配置
│   │   └── main.ts        # 入口文件
│   ├── package.json
│   └── vite.config.ts
├── backend/               # Python 后端应用
│   ├── app/
│   │   ├── server.py      # FastAPI 服务器
│   │   ├── agent.py       # LangChain 代理
│   │   └── config.py      # 配置管理
│   ├── requirements.txt
│   └── main.py            # 入口文件
├── start.sh               # 一键启动脚本
└── README.md
```