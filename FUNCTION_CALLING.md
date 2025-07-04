# Function Calling 功能说明

## 概述

本AI Agent后端现已支持完整的OpenAI Function Calling API，包括：

- ✅ 新版 `tools` 和 `tool_choice` 参数 (推荐)
- ✅ 旧版 `functions` 和 `function_call` 参数 (兼容性支持)
- ✅ 完全兼容OpenAI API格式
- ✅ 透传到底层DeepSeek模型
- ⚠️  流式模式暂不支持Function Calling

## API使用方法

### 1. 使用Tools API (推荐)

```python
import httpx
import json

# 定义工具函数
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定城市的天气信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称，例如：北京、上海"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "温度单位"
                    }
                },
                "required": ["city"]
            }
        }
    }
]

# 发送请求
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/v1/chat/completions",
        json={
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": "北京今天天气怎么样？"}
            ],
            "tools": tools,
            "tool_choice": "auto"  # auto, none, 或指定函数
        }
    )
```

### 2. 使用Legacy Functions API

```python
# 使用旧版functions格式
functions = [
    {
        "name": "calculate",
        "description": "执行数学计算",
        "parameters": {
            "type": "object", 
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "要计算的数学表达式"
                }
            },
            "required": ["expression"]
        }
    }
]

# 发送请求
response = await client.post(
    "http://localhost:8000/v1/chat/completions",
    json={
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": "计算 15 * 8 + 23"}
        ],
        "functions": functions,
        "function_call": "auto"
    }
)
```

## 响应格式

### 当模型决定调用函数时

```json
{
    "id": "chatcmpl-abc123",
    "object": "chat.completion",
    "created": 1234567890,
    "model": "deepseek-chat",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": null,
                "tool_calls": [
                    {
                        "id": "call_abc123",
                        "type": "function",
                        "function": {
                            "name": "get_weather",
                            "arguments": "{\"city\": \"北京\", \"unit\": \"celsius\"}"
                        }
                    }
                ]
            },
            "finish_reason": "tool_calls"
        }
    ],
    "usage": {
        "prompt_tokens": 50,
        "completion_tokens": 20,
        "total_tokens": 70
    }
}
```

### 当模型直接回复时

```json
{
    "id": "chatcmpl-def456",
    "object": "chat.completion", 
    "created": 1234567890,
    "model": "deepseek-chat",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "我无法获取实时天气信息，建议您查看天气预报应用。"
            },
            "finish_reason": "stop"
        }
    ],
    "usage": {
        "prompt_tokens": 30,
        "completion_tokens": 25,
        "total_tokens": 55
    }
}
```

## 多轮Function Calling

如果需要执行函数并继续对话：

```python
# 第一轮：用户请求
messages = [
    {"role": "user", "content": "北京今天天气怎么样？"}
]

# AI回复包含tool_calls...

# 第二轮：添加函数执行结果
messages.extend([
    {
        "role": "assistant",
        "content": null,
        "tool_calls": [
            {
                "id": "call_abc123",
                "type": "function", 
                "function": {
                    "name": "get_weather",
                    "arguments": "{\"city\": \"北京\"}"
                }
            }
        ]
    },
    {
        "role": "tool",
        "tool_call_id": "call_abc123",
        "content": "北京今天晴天，温度15-25°C"
    }
])

# 第三轮：AI总结回复
response = await client.post(
    "http://localhost:8000/v1/chat/completions",
    json={
        "model": "deepseek-chat",
        "messages": messages,
        "tools": tools
    }
)
```

## Tool Choice 选项

- `"auto"`: 模型自动决定是否调用函数
- `"none"`: 强制模型不调用任何函数
- `{"type": "function", "function": {"name": "function_name"}}`: 强制调用指定函数

## 参数类型支持

支持所有JSON Schema类型：

```python
"parameters": {
    "type": "object",
    "properties": {
        "string_param": {"type": "string"},
        "number_param": {"type": "number"},
        "integer_param": {"type": "integer"},
        "boolean_param": {"type": "boolean"},
        "array_param": {
            "type": "array",
            "items": {"type": "string"}
        },
        "enum_param": {
            "type": "string",
            "enum": ["option1", "option2"]
        }
    },
    "required": ["string_param"]
}
```

## 测试

运行测试脚本：

```bash
cd /path/to/project
python test_function_calling.py
```

## 注意事项

1. **流式模式**：Function Calling 暂不支持流式 (`stream: true`)
2. **模型支持**：需要底层模型支持Function Calling (DeepSeek V3支持)
3. **错误处理**：如果函数定义有误，会返回相应错误信息
4. **性能**：Function Calling 请求会直接透传到底层API，绕过部分LangChain处理

## 前端集成

前端可以直接使用现有的API接口，只需在请求中添加`tools`或`functions`参数：

```typescript
// 在frontend/src/stores/api.ts中添加
export async function sendMessageWithTools(
    message: string,
    tools: any[],
    conversationHistory: any[] = []
) {
    const response = await fetch('/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            model: 'deepseek-chat',
            messages: [
                ...conversationHistory,
                { role: 'user', content: message }
            ],
            tools: tools,
            tool_choice: 'auto'
        })
    });
    
    return response.json();
}
```

Function Calling功能现已完全集成到后端，与OpenAI API完全兼容！ 