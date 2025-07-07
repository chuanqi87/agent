# LangServe Agent Backend

基于 LangChain 和 LangServe 构建的 AI Agent 后端，提供 OpenAI 兼容的 API 接口，支持流式响应和端侧工具调用。

## 功能特性

- ✅ **OpenAI 兼容 API**: 完全兼容 OpenAI ChatCompletion API 格式
- ✅ **流式响应**: 支持实时流式输出，提供更好的用户体验
- ✅ **工具调用**: 内置多种工具，支持端侧工具调用
- ✅ **LangChain 集成**: 基于 LangChain 框架，易于扩展
- ✅ **FastAPI 后端**: 高性能异步 API 服务器
- ✅ **可配置**: 支持环境变量配置
- ✅ **完整文档**: 自动生成 API 文档

## 技术栈

- **LangChain**: AI 应用开发框架
- **LangServe**: LangChain 服务部署工具
- **FastAPI**: 现代、高性能 Python Web 框架
- **Pydantic**: 数据验证和设置管理
- **Uvicorn**: ASGI 服务器

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd langserve-agent-backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或者
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，设置您的 OpenAI API Key
vim .env
```

必需的环境变量：
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. 启动服务器

```bash
# 方式1：使用启动脚本
chmod +x run.sh
./run.sh

# 方式2：直接运行
python main.py

# 方式3：使用 uvicorn
uvicorn app.server:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 验证服务

访问以下地址验证服务是否正常：

- 健康检查: http://localhost:8000/health
- API 文档: http://localhost:8000/docs
- OpenAPI 规范: http://localhost:8000/openapi.json

## API 接口

### 主要端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/v1/models` | GET | 列出可用模型 |
| `/v1/chat/completions` | POST | 聊天完成（OpenAI 兼容） |
| `/v1/tools` | GET | 列出可用工具 |
| `/v1/tools/execute` | POST | 执行工具 |
| `/v1/agent/info` | GET | 获取 Agent 信息 |

### 聊天完成接口

#### 非流式请求

```bash
curl -X POST "http://localhost:8000/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {"role": "user", "content": "你好！"}
    ]
  }'
```

#### 流式请求

```bash
curl -X POST "http://localhost:8000/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {"role": "user", "content": "请介绍一下你的能力"}
    ],
    "stream": true
  }'
```

#### 带工具调用

```bash
curl -X POST "http://localhost:8000/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {"role": "user", "content": "请帮我计算 15 * 23 + 45"}
    ],
    "tools": [
      {
        "type": "function",
        "function": {
          "name": "calculator",
          "description": "用于执行数学计算的工具",
          "parameters": {
            "type": "object",
            "properties": {
              "query": {
                "type": "string",
                "description": "工具的输入参数"
              }
            },
            "required": ["query"]
          }
        }
      }
    ]
  }'
```

## 内置工具

系统内置了以下工具：

### 计算器工具
- **名称**: `calculator`
- **描述**: 执行数学计算
- **用法**: 输入数学表达式，如 "2 + 3 * 4"

### 时间工具
- **名称**: `current_time`
- **描述**: 获取当前日期和时间
- **用法**: 无需参数

### 天气工具
- **名称**: `weather`
- **描述**: 查询城市天气信息（示例）
- **用法**: 输入城市名称

### 网络搜索工具
- **名称**: `web_search`
- **描述**: 网络搜索工具（示例）
- **用法**: 输入搜索关键词

## 客户端使用示例

### Python 客户端

```python
import asyncio
import httpx
import json

async def test_chat():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/v1/chat/completions",
            json={
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "user", "content": "你好！"}
                ]
            }
        )
        print(response.json())

asyncio.run(test_chat())
```

### OpenAI SDK 兼容

```python
import openai

# 设置 base_url 指向本地服务
openai.api_base = "http://localhost:8000/v1"
openai.api_key = "dummy"  # 不需要真实 key

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "你好！"}
    ]
)

print(response.choices[0].message.content)
```

### 流式响应示例

```python
import asyncio
import httpx
import json

async def test_stream():
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST",
            "http://localhost:8000/v1/chat/completions",
            json={
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "user", "content": "请介绍一下你的能力"}
                ],
                "stream": True
            }
        ) as response:
            async for chunk in response.aiter_text():
                if chunk.strip():
                    for line in chunk.strip().split('\n'):
                        if line.startswith('data: '):
                            data = line[6:]
                            if data == '[DONE]':
                                break
                            try:
                                parsed = json.loads(data)
                                if 'choices' in parsed:
                                    delta = parsed['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        print(delta['content'], end='', flush=True)
                            except json.JSONDecodeError:
                                pass

asyncio.run(test_stream())
```

## 项目结构

```
langserve-agent-backend/
├── app/
│   ├── __init__.py
│   ├── config.py          # 配置管理
│   ├── models.py          # 数据模型
│   ├── tools.py           # 工具定义
│   ├── chains.py          # LangChain 链
│   └── server.py          # FastAPI 服务器
├── main.py                # 主程序入口
├── requirements.txt       # 依赖包
├── .env.example          # 环境变量模板
├── run.sh                # 启动脚本
├── client_example.py     # 客户端示例
└── README.md             # 项目文档
```

## 配置说明

### 环境变量

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| `OPENAI_API_KEY` | OpenAI API 密钥 | 必需 |
| `OPENAI_BASE_URL` | OpenAI API 基础URL | https://api.openai.com/v1 |
| `HOST` | 服务器监听地址 | 0.0.0.0 |
| `PORT` | 服务器端口 | 8000 |
| `DEFAULT_MODEL` | 默认模型 | gpt-3.5-turbo |
| `MAX_TOKENS` | 最大令牌数 | 4096 |
| `TEMPERATURE` | 温度参数 | 0.7 |
| `AGENT_NAME` | Agent 名称 | LangServe Agent |
| `AGENT_DESCRIPTION` | Agent 描述 | A powerful AI agent... |
| `ENABLE_TOOLS` | 启用工具功能 | true |

## 扩展开发

### 添加新工具

1. 在 `app/tools.py` 中继承 `BaseTool` 类：

```python
class MyCustomTool(BaseTool):
    name = "my_tool"
    description = "我的自定义工具"
    
    def _run(self, query: str) -> str:
        # 实现工具逻辑
        return f"处理结果: {query}"
    
    async def _arun(self, query: str) -> str:
        return self._run(query)
```

2. 在 `ToolManager` 中注册工具：

```python
def __init__(self):
    self.tools = {
        # 现有工具...
        "my_tool": MyCustomTool()
    }
```

### 自定义模型

修改 `app/chains.py` 中的 `AgentChain` 类，替换或扩展 LLM 配置。

### 添加中间件

在 `app/server.py` 中添加 FastAPI 中间件：

```python
@app.middleware("http")
async def custom_middleware(request: Request, call_next):
    # 中间件逻辑
    response = await call_next(request)
    return response
```

## 部署

### Docker 部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
```

### 生产环境

```bash
# 使用 gunicorn 部署
pip install gunicorn
gunicorn app.server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 故障排除

### 常见问题

1. **ImportError**: 确保已安装所有依赖包
2. **API Key 错误**: 检查 `.env` 文件中的 `OPENAI_API_KEY`
3. **端口占用**: 修改 `PORT` 环境变量
4. **工具调用失败**: 检查工具参数格式

### 日志调试

服务器会输出详细的日志信息，包括：
- 请求处理时间
- 错误堆栈跟踪
- 工具执行结果

### 性能优化

- 调整 `MAX_TOKENS` 和 `TEMPERATURE` 参数
- 使用更快的模型（如 gpt-3.5-turbo）
- 启用请求缓存
- 使用负载均衡

## 许可证

本项目基于 MIT 许可证开源。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题，请通过以下方式联系：

- 创建 GitHub Issue
- 邮件联系: [your-email@example.com]

---

**注意**: 请确保您的 OpenAI API Key 安全，不要将其提交到版本控制系统中。