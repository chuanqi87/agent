#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import json
import asyncio
import time
import uuid
from typing import Dict, Any, List, Optional
from .config import get_settings
from .passthrough_agent import DirectAgent

# 创建FastAPI应用
app = FastAPI(
    title="AI Agent API (Direct Passthrough)",
    description="直接透传消息给大模型的简化AI Agent",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    servers=[
        {"url": "http://localhost:8000", "description": "本地开发服务器"},
    ]
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 获取配置
settings = get_settings()
model_config = settings.get_active_model_config()

print(f"🚀 初始化透传Agent - {model_config['provider'].upper()} {model_config['model']}")
print(f"📡 API Base URL: {model_config['base_url']}")
print(f"🔑 API Key: {'*' * 10 + model_config['api_key'][-4:] if model_config['api_key'] else 'NOT SET'}")

# 创建透传代理实例
try:
    agent = DirectAgent()
    print("✅ 透传Agent初始化成功")
except Exception as e:
    print(f"❌ 透传Agent初始化失败: {e}")
    agent = None

@app.get("/")
async def root():
    """根路径信息"""
    print("📍 访问根路径")
    return {
        "status": "ok",
        "service": "AI Agent Backend (Direct Passthrough)",
        "version": "1.0.0",
        "provider": model_config["provider"],
        "model": model_config["model"],
        "endpoints": {
            "health": "/health",
            "models": "/v1/models",
            "chat": "/v1/chat/completions"
        }
    }

@app.get("/health")
async def health_check():
    """健康检查接口"""
    print("🏥 健康检查请求")
    return {
        "status": "healthy",
        "service": "AI Agent Backend (Direct Passthrough)",
        "version": "1.0.0",
        "agent_available": agent is not None,
        "provider": model_config["provider"],
        "model": model_config["model"]
    }

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    """OpenAI兼容的聊天完成端点，完全透传"""
    request_id = str(uuid.uuid4())[:8]
    client_ip = request.client.host if request.client else "unknown"
    
    print(f"\n🚀 [{request_id}] 收到聊天完成请求")
    print(f"🌐 [{request_id}] 客户端IP: {client_ip}")
    print(f"📋 [{request_id}] 请求头: {dict(request.headers)}")
    
    if not agent:
        print(f"❌ [{request_id}] Agent未初始化")
        return {"error": "Agent not initialized"}
    
    try:
        # 获取请求数据
        request_data = await request.json()
        print(f"📦 [{request_id}] 请求数据大小: {len(json.dumps(request_data))} 字符")
        
        # 提取基本参数
        messages = request_data.get("messages", [])
        if not messages:
            print(f"❌ [{request_id}] 缺少messages参数")
            return {"error": "Messages are required"}
        
        stream = request_data.get("stream", False)
        tools = request_data.get("tools")
        
        # 打印请求摘要
        print(f"📝 [{request_id}] 消息数量: {len(messages)}")
        print(f"🔧 [{request_id}] 工具数量: {len(tools) if tools else 0}")
        print(f"🌊 [{request_id}] 流式模式: {stream}")
        
        # 打印每条消息的基本信息
        for i, msg in enumerate(messages):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            content_preview = content[:50] + "..." if len(content) > 50 else content
            print(f"💬 [{request_id}] 消息{i+1}: {role} - {content_preview}")
        
        # 提取其他参数（全部透传）
        other_params = {k: v for k, v in request_data.items() 
                       if k not in ["messages", "stream", "tools"]}
        
        if other_params:
            print(f"⚙️  [{request_id}] 其他参数: {other_params}")
        
        # 流式响应
        if stream:
            print(f"🌊 [{request_id}] 开始流式响应")
            
            async def stream_generator():
                """流式数据生成器"""
                try:
                    chunk_sent_count = 0
                    async for chunk in agent.stream_chat(messages, tools, **other_params):
                        chunk_sent_count += 1
                        # 每100个chunk打印一次发送进度
                        if chunk_sent_count % 100 == 0:
                            print(f"📡 [{request_id}] 已发送 {chunk_sent_count} 个chunk到前端")
                        yield chunk
                    print(f"✅ [{request_id}] 流式响应发送完成，共发送 {chunk_sent_count} 个chunk")
                except Exception as e:
                    print(f"❌ [{request_id}] 流式生成器异常: {str(e)}")
                    # 发送错误信息
                    error_chunk = {
                        "id": f"chatcmpl-{request_id}",
                        "object": "chat.completion.chunk",
                        "created": int(time.time()),
                        "model": model_config["model"],
                        "choices": [{
                            "index": 0,
                            "delta": {"content": f"错误: {str(e)}"},
                            "finish_reason": "stop"
                        }]
                    }
                    yield f"data: {json.dumps(error_chunk)}\n\n"
                    yield "data: [DONE]\n\n"
            
            return StreamingResponse(
                stream_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                    "X-Request-ID": request_id,
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization"
                }
            )
        
        # 非流式响应
        print(f"📝 [{request_id}] 开始非流式响应")
        result = await agent.chat(messages, tools, **other_params)
        
        print(f"✅ [{request_id}] 请求处理完成")
        return result
        
    except json.JSONDecodeError as e:
        print(f"❌ [{request_id}] JSON解析错误: {str(e)}")
        return {"error": f"JSON解析失败: {str(e)}"}
    except Exception as e:
        print(f"❌ [{request_id}] 聊天完成错误: {str(e)}")
        return {"error": f"聊天完成失败: {str(e)}"}

@app.get("/v1/models")
async def list_models():
    """获取可用模型列表 (OpenAI兼容)"""
    print("📋 获取模型列表请求")
    return {
        "object": "list",
        "data": [
            {
                "id": model_config["model"],
                "object": "model",
                "created": 1677610602,
                "owned_by": model_config["provider"],
                "permission": [],
                "root": model_config["model"],
                "parent": None,
            }
        ]
    }

@app.middleware("http")
async def add_headers(request: Request, call_next):
    """添加响应头和请求日志"""
    start_time = time.time()
    
    # 记录请求开始
    print(f"📥 请求开始: {request.method} {request.url}")
    
    response = await call_next(request)
    
    # 记录请求结束
    process_time = time.time() - start_time
    print(f"📤 请求结束: {request.method} {request.url} - {response.status_code} - {process_time:.2f}s")
    
    response.headers["X-Powered-By"] = "Direct-Passthrough-Agent"
    response.headers["X-Agent-Version"] = "1.0.0"
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理操作"""
    if agent:
        await agent.close()
        print("🔒 应用关闭，Agent资源已清理")

def create_app():
    """创建应用实例"""
    return app 