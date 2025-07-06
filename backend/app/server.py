#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, StreamingResponse
import json
import asyncio

# langserve imports
from langserve import add_routes

from .agent import ChatAgent
from .config import get_settings

# 创建FastAPI应用
app = FastAPI(
    title="AI Agent API (LangServe + OpenAI Compatible)",
    description="基于LangServe的AI Agent聊天服务，完全兼容OpenAI API协议",
    version="1.0.0",
    docs_url=None,  # 禁用文档以避免OpenAPI schema问题
    redoc_url=None,
    servers=[
        {"url": "http://localhost:8000", "description": "本地开发服务器"},
    ]
)

# 配置CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源
    allow_credentials=False,  # 当allow_origins为*时，必须设为False
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建聊天代理实例
print("🚀 正在初始化 AI Agent...")
try:
    chat_agent = ChatAgent()
    print("✅ AI Agent 初始化成功")
except Exception as e:
    print(f"❌ AI Agent 初始化失败: {e}")
    chat_agent = None

# 获取LangChain链
chain = chat_agent.get_chain() if chat_agent else None

# 使用langserve添加OpenAI兼容的路由
if chain:
    print("🔗 正在添加 LangServe 路由...")
    
    # 添加聊天完成端点 (简化配置)
    add_routes(
        app,
        chain,
        path="/v1/chat/completions",
        enable_feedback_endpoint=False,
        enable_public_trace_link_endpoint=False
    )
    
    print("✅ LangServe 路由添加成功")
else:
    print("❌ 无法添加 LangServe 路由，Agent 初始化失败")

@app.get("/")
async def root():
    """根路径信息"""
    return {
        "status": "ok",
        "service": "AI Agent Backend (LangServe)",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health", 
            "models": "/v1/models",
            "chat": "/v1/chat/completions"
        }
    }

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "AI Agent Backend (LangServe)",
        "version": "1.0.0",
        "framework": "LangChain + LangServe",
        "agent_available": chat_agent is not None,
        "provider": chat_agent.get_model_info()["provider"] if chat_agent else "unknown",
        "model": chat_agent.get_model_info()["model"] if chat_agent else "unknown"
    }

async def generate_stream_response(user_input: str, model_info: dict, tools: list = None):
    """生成流式响应，支持工具调用"""
    try:
        chat_id = f"chatcmpl-{__import__('uuid').uuid4().hex[:8]}"
        created_time = int(__import__('time').time())
        
        # 发送开始chunk
        yield f"data: {json.dumps({'id': chat_id, 'object': 'chat.completion.chunk', 'created': created_time, 'model': model_info['model'], 'choices': [{'index': 0, 'delta': {'role': 'assistant'}, 'finish_reason': None}]})}\n\n"
        
        # 调用agent链
        chain = chat_agent.get_chain()
        result = await chain.ainvoke({"input": user_input})
        
        response_content = result.get("output", "")
        
        # 检查是否有工具调用（通过检查agent的中间步骤）
        intermediate_steps = result.get("intermediate_steps", [])
        
        if intermediate_steps:
            # 有工具调用，发送工具调用chunks
            for step in intermediate_steps:
                action, observation = step
                if hasattr(action, 'tool') and hasattr(action, 'tool_input'):
                    # 发送工具调用chunk
                    tool_call_chunk = {
                        "id": chat_id,
                        "object": "chat.completion.chunk",
                        "created": created_time,
                        "model": model_info["model"],
                        "choices": [{
                            "index": 0,
                            "delta": {
                                "tool_calls": [{
                                    "index": 0,
                                    "id": f"call_{__import__('uuid').uuid4().hex[:8]}",
                                    "type": "function",
                                    "function": {
                                        "name": action.tool,
                                        "arguments": json.dumps(action.tool_input)
                                    }
                                }]
                            },
                            "finish_reason": None
                        }]
                    }
                    yield f"data: {json.dumps(tool_call_chunk)}\n\n"
                    await asyncio.sleep(0.05)
        
        # 发送响应内容chunks
        if response_content:
            # 按字符分割实现真正的流式效果
            for i, char in enumerate(response_content):
                chunk_data = {
                    "id": chat_id,
                    "object": "chat.completion.chunk",
                    "created": created_time,
                    "model": model_info["model"],
                    "choices": [{
                        "index": 0,
                        "delta": {"content": char},
                        "finish_reason": None
                    }]
                }
                yield f"data: {json.dumps(chunk_data)}\n\n"
                await asyncio.sleep(0.01)  # 打字效果
        
        # 发送结束chunk
        end_chunk = {
            "id": chat_id,
            "object": "chat.completion.chunk",
            "created": created_time,
            "model": model_info["model"],
            "choices": [{
                "index": 0,
                "delta": {},
                "finish_reason": "tool_calls" if intermediate_steps else "stop"
            }]
        }
        yield f"data: {json.dumps(end_chunk)}\n\n"
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        print(f"❌ 流式响应生成错误: {e}")
        error_chunk = {
            "id": f"chatcmpl-{__import__('uuid').uuid4().hex[:8]}",
            "object": "chat.completion.chunk",
            "created": int(__import__('time').time()),
            "model": model_info.get("model", "unknown"),
            "choices": [{
                "index": 0,
                "delta": {"content": f"错误: {str(e)}"},
                "finish_reason": "stop"
            }]
        }
        yield f"data: {json.dumps(error_chunk)}\n\n"
        yield "data: [DONE]\n\n"

@app.post("/v1/chat/completions")
async def openai_chat_completions(request: dict):
    """OpenAI兼容的聊天完成端点，支持流式和非流式"""
    if not chat_agent:
        return {"error": "Agent not initialized"}
    
    try:
        # 提取参数
        messages = request.get("messages", [])
        if not messages:
            return {"error": "Messages are required"}
        
        stream = request.get("stream", False)
        user_input = messages[-1].get("content", "")
        model_info = chat_agent.get_model_info()
        
        # 流式响应
        if stream:
            tools = request.get("tools", [])
            return StreamingResponse(
                generate_stream_response(user_input, model_info, tools),
                media_type="text/event-stream"
            )
        
        # 非流式响应
        chain = chat_agent.get_chain()
        result = await chain.ainvoke({"input": user_input})
        
        return {
            "id": f"chatcmpl-{__import__('uuid').uuid4().hex[:8]}",
            "object": "chat.completion",
            "created": int(__import__('time').time()),
            "model": model_info["model"],
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": result.get("output", "")
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }
        
    except Exception as e:
        print(f"❌ 聊天完成错误: {e}")
        return {"error": f"聊天完成失败: {str(e)}"}

@app.get("/v1/models")
async def list_models():
    """获取可用模型列表 (OpenAI兼容)"""
    if not chat_agent:
        return {"error": "Agent not initialized"}
    
    model_info = chat_agent.get_model_info()
    provider = model_info["provider"]
    model_name = model_info["model"]
    
    # 返回OpenAI兼容的模型列表
    return {
        "object": "list",
        "data": [
            {
                "id": model_name,
                "object": "model",
                "created": 1677610602,
                "owned_by": provider,
                "permission": [],
                "root": model_name,
                "parent": None,
            }
        ]
    }



# 中间件：添加LangServe相关的头部信息
@app.middleware("http")
async def add_langserve_headers(request: Request, call_next):
    """添加LangServe相关头部信息"""
    response = await call_next(request)
    
    # 添加服务识别头部
    response.headers["X-Powered-By"] = "LangServe"
    response.headers["X-Agent-Version"] = "1.0.0"
    
    return response

# 导出应用实例
def create_app():
    """创建应用实例"""
    return app 