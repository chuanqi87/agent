# 模型切换功能说明

## 概述

uni-agent 现已支持多种AI模型提供商的动态切换，包括：

- ✅ **Gemini** (Google) - 推荐使用 gemini-2.0-flash-exp
- ✅ **DeepSeek** - 支持 deepseek-chat, deepseek-reasoner
- ✅ **OpenAI** - 支持 gpt-4, gpt-4-turbo, gpt-3.5-turbo
- ✅ **环境变量配置** - 支持通过.env文件配置
- ✅ **API动态切换** - 运行时切换模型，无需重启
- ✅ **Function Calling** - 所有模型都支持function calling

## 快速开始

### 1. 配置环境变量

复制环境变量示例文件：
```bash
cp backend/env.example backend/.env
```

编辑 `backend/.env` 文件：
```bash
# 设置使用Gemini模型
MODEL_PROVIDER=gemini

# 设置Gemini API密钥
GEMINI_API_KEY=your_gemini_api_key_here

# 其他配置保持默认
GEMINI_MODEL=gemini-2.0-flash-exp
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta
```

### 2. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 3. 启动服务

```bash
python -m backend.main
```

### 4. 验证配置

访问 http://localhost:8000/v1/model/current 查看当前模型信息。

## 支持的模型

### Gemini (推荐)

**获取API密钥**: https://aistudio.google.com/app/apikey

```bash
MODEL_PROVIDER=gemini
GEMINI_API_KEY=your_api_key
GEMINI_MODEL=gemini-2.0-flash-exp  # 或 gemini-1.5-pro
```

**可用模型**:
- `gemini-2.0-flash-exp` - 最新实验版本，性能出色
- `gemini-1.5-pro` - 稳定版本，适合生产使用
- `gemini-1.5-flash` - 快速版本，响应更快

### DeepSeek

**获取API密钥**: https://platform.deepseek.com/

```bash
MODEL_PROVIDER=deepseek
DEEPSEEK_API_KEY=your_api_key
DEEPSEEK_MODEL=deepseek-chat  # 或 deepseek-reasoner
```

### OpenAI

**获取API密钥**: https://platform.openai.com/

```bash
MODEL_PROVIDER=openai
OPENAI_API_KEY_ORIGINAL=your_api_key
OPENAI_MODEL_ORIGINAL=gpt-4
```

## API接口

### 获取当前模型信息

```bash
GET /v1/model/current
```

响应示例：
```json
{
  "current_model": {
    "provider": "gemini",
    "model": "gemini-2.0-flash-exp",
    "base_url": "https://generativelanguage.googleapis.com/v1beta",
    "has_api_key": true
  },
  "memory_stats": {
    "total_messages": 10,
    "user_messages": 5,
    "ai_messages": 5,
    "memory_window": 10,
    "current_model": "gemini-2.0-flash-exp",
    "current_provider": "gemini"
  },
  "timestamp": 1234567890
}
```

### 动态切换模型

```bash
POST /v1/model/switch
Content-Type: application/json

{
  "provider": "gemini",
  "api_key": "your_api_key",  # 可选，不提供则使用环境变量
  "model": "gemini-2.0-flash-exp"  # 可选，不提供则使用默认
}
```

响应示例：
```json
{
  "success": true,
  "message": "成功切换到 GEMINI",
  "new_model": {
    "provider": "gemini",
    "model": "gemini-2.0-flash-exp",
    "base_url": "https://generativelanguage.googleapis.com/v1beta",
    "has_api_key": true
  }
}
```

### 获取可用模型列表

```bash
GET /v1/models
```

## 前端集成

前端会自动适应后端的模型切换，无需修改代码。所有现有功能（聊天、流式输出、markdown渲染、function calling）都完全兼容。

### 添加模型切换UI（可选）

可以在前端添加模型选择器：

```typescript
// 在 api store 中添加
export async function getCurrentModel() {
  const response = await fetch('/v1/model/current')
  return response.json()
}

export async function switchModel(provider: string, apiKey?: string, model?: string) {
  const response = await fetch('/v1/model/switch', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ provider, api_key: apiKey, model })
  })
  return response.json()
}
```

## 性能对比

| 模型 | 响应速度 | 推理能力 | 中文支持 | Function Calling | 价格 |
|------|----------|----------|----------|------------------|------|
| Gemini 2.0 Flash | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ | 💰💰 |
| DeepSeek Chat | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ | 💰 |
| GPT-4 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ | 💰💰💰 |

## 测试

运行测试脚本验证模型切换功能：

```bash
python test_model_switch.py
```

## 故障排除

### 1. API密钥错误
```
错误: 请在.env文件中设置GEMINI_API_KEY
解决: 检查环境变量文件中的API密钥配置
```

### 2. 模型不支持
```
错误: 底层GEMINI API调用失败
解决: 检查模型名称是否正确，或切换到其他模型
```

### 3. 网络连接问题
```
错误: 连接超时
解决: 检查网络连接，或使用代理
```

### 4. Function Calling不工作
```
问题: 工具调用失败
解决: 确保使用的模型支持function calling，Gemini 2.0需要特定配置
```

## 高级配置

### 自定义模型端点

如果使用第三方API代理，可以自定义base_url：

```bash
# 使用自定义Gemini代理
GEMINI_BASE_URL=https://your-proxy.com/v1beta

# 使用自定义DeepSeek代理  
DEEPSEEK_BASE_URL=https://your-proxy.com/v1
```

### 批量模型配置

在一个项目中同时配置多个模型，可以快速切换：

```bash
# 环境变量中配置所有模型
MODEL_PROVIDER=gemini

# 所有API密钥
GEMINI_API_KEY=gemini_key_here
DEEPSEEK_API_KEY=deepseek_key_here  
OPENAI_API_KEY_ORIGINAL=openai_key_here

# 然后通过API动态切换
```

### 模型参数调优

不同模型的最佳参数配置：

```python
# Gemini
{
    "temperature": 0.7,
    "max_tokens": 2000,
    "top_p": 0.9
}

# DeepSeek  
{
    "temperature": 0.8,
    "max_tokens": 4000,
    "top_p": 1.0
}

# OpenAI
{
    "temperature": 0.7,
    "max_tokens": 2000,
    "top_p": 1.0
}
```

## 总结

现在您的uni-agent支持完整的模型切换功能！可以：

1. 🚀 **即时切换** - API或环境变量动态切换模型
2. 🔧 **完全兼容** - 所有现有功能无缝支持
3. 💰 **成本优化** - 根据需求选择最合适的模型
4. 🌟 **性能提升** - Gemini 2.0 Flash提供卓越性能

推荐使用**Gemini 2.0 Flash**作为主要模型，它在速度、质量和成本之间提供了最佳平衡。 