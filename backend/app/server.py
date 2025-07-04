#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .agent import ChatAgent
from .config import get_settings
from .openai_api import openai_router, set_chat_agent

# 创建FastAPI应用
app = FastAPI(
    title="AI Agent API (OpenAI Compatible)",
    description="基于LangChain的AI Agent聊天服务，完全兼容OpenAI API协议",
    version="0.1.0",
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
chat_agent = ChatAgent()

# 设置OpenAI API的chat agent
set_chat_agent(chat_agent)

# 注册OpenAI兼容的路由
app.include_router(openai_router, tags=["OpenAI Compatible API"])

@app.get("/")
async def root():
    """根路径健康检查"""
    return {"message": "AI Agent 后端服务运行中", "status": "healthy"}

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "AI Agent Backend (LangChain)",
        "version": "0.1.0",
        "framework": "LangChain + DeepSeek"
    }

@app.get("/memory/stats")
async def get_memory_stats():
    """获取对话记忆统计"""
    try:
        stats = chat_agent.get_memory_stats()
        return {"status": "success", "data": stats}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/memory/clear")
async def clear_memory():
    """清除对话记忆"""
    try:
        chat_agent.clear_history()
        return {"status": "success", "message": "对话记忆已清除"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/conversation/summary")
async def get_conversation_summary():
    """获取对话摘要"""
    try:
        summary = await chat_agent.get_conversation_summary()
        return {"status": "success", "summary": summary}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 导出应用实例
def create_app():
    """创建应用实例"""
    return app 