from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from typing import Dict, Any, List, Optional
import json
import asyncio
import logging
from datetime import datetime
import traceback

from .config import config
from .models import (
    ChatCompletionRequest, 
    ChatCompletionResponse, 
    ChatCompletionStreamResponse,
    ModelListResponse,
    ModelInfo,
    HealthResponse,
    ErrorResponse
)
from .chains import agent_chain
from .tools import tool_manager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="LangServe Agent API",
    description="OpenAI兼容的AI Agent API，基于LangChain和LangServe构建",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 自定义OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="LangServe Agent API",
        version="1.0.0",
        description="OpenAI兼容的AI Agent API，支持流式响应和工具调用",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://langchain.com/static/langchain-logo.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.get("/", response_model=HealthResponse)
async def root():
    """根路径健康检查"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=int(datetime.now().timestamp())
    )

@app.get("/health", response_model=HealthResponse)
async def health():
    """健康检查端点"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=int(datetime.now().timestamp())
    )

@app.get("/v1/models", response_model=ModelListResponse)
async def list_models():
    """列出可用的模型"""
    models = [
        ModelInfo(
            id=config.DEFAULT_MODEL,
            owned_by="langserve"
        ),
        ModelInfo(
            id="gpt-3.5-turbo",
            owned_by="langserve"
        ),
        ModelInfo(
            id="gpt-4",
            owned_by="langserve"
        ),
        ModelInfo(
            id="gpt-4-turbo",
            owned_by="langserve"
        )
    ]
    
    return ModelListResponse(data=models)

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """聊天完成接口 - OpenAI兼容"""
    try:
        # 验证请求
        if not request.messages:
            raise HTTPException(
                status_code=400,
                detail="Messages are required"
            )
        
        # 记录请求
        logger.info(f"收到聊天请求: 模型={request.model}, 流式={request.stream}, 消息数={len(request.messages)}")
        
        # 处理流式请求
        if request.stream:
            return StreamingResponse(
                agent_chain.process_request(request),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Allow-Methods": "*"
                }
            )
        else:
            # 处理非流式请求
            response = await agent_chain.process_non_streaming(request)
            
            # 检查是否有错误
            if "error" in response:
                raise HTTPException(
                    status_code=500,
                    detail=response["error"]["message"]
                )
            
            return response
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"处理聊天请求时发生错误: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/v1/tools")
async def list_tools():
    """列出可用的工具"""
    try:
        tools = tool_manager.get_tool_schemas()
        return {
            "tools": tools,
            "count": len(tools)
        }
    except Exception as e:
        logger.error(f"获取工具列表时发生错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get tools: {str(e)}"
        )

@app.post("/v1/tools/execute")
async def execute_tool(request: Dict[str, Any]):
    """执行工具"""
    try:
        tool_name = request.get("tool_name")
        arguments = request.get("arguments", "")
        
        if not tool_name:
            raise HTTPException(
                status_code=400,
                detail="tool_name is required"
            )
        
        # 执行工具
        result = await tool_manager.aexecute_tool(tool_name, arguments)
        
        return {
            "tool_name": tool_name,
            "arguments": arguments,
            "result": result,
            "timestamp": int(datetime.now().timestamp())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"执行工具时发生错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Tool execution failed: {str(e)}"
        )

@app.get("/v1/agent/info")
async def agent_info():
    """获取Agent信息"""
    return {
        "name": config.AGENT_NAME,
        "description": config.AGENT_DESCRIPTION,
        "model": config.DEFAULT_MODEL,
        "tools_enabled": config.ENABLE_TOOLS,
        "available_tools": len(tool_manager.get_all_tools()),
        "version": "1.0.0"
    }

@app.get("/docs")
async def get_docs():
    """API文档"""
    return {"message": "API文档可在 /docs 路径访问"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    logger.error(f"未处理的异常: {str(exc)}")
    logger.error(traceback.format_exc())
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "message": f"Internal server error: {str(exc)}",
                "type": "internal_error"
            }
        }
    )

# 启动时的验证
@app.on_event("startup")
async def startup_event():
    """启动时验证配置"""
    try:
        # 验证配置
        config.validate()
        logger.info("配置验证通过")
        
        # 初始化Agent链
        logger.info("初始化Agent链...")
        
        # 记录工具信息
        tools = tool_manager.get_all_tools()
        logger.info(f"已加载 {len(tools)} 个工具")
        for tool in tools:
            logger.info(f"- {tool.name}: {tool.description}")
        
        logger.info("LangServe Agent API 启动成功")
        
    except Exception as e:
        logger.error(f"启动时发生错误: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """关闭时的清理"""
    logger.info("LangServe Agent API 正在关闭...")
    # 在这里可以添加清理逻辑
    logger.info("LangServe Agent API 已关闭")

# 中间件：请求日志
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """请求日志中间件"""
    start_time = datetime.now()
    
    # 记录请求开始
    logger.info(f"请求开始: {request.method} {request.url}")
    
    try:
        response = await call_next(request)
        
        # 计算处理时间
        process_time = (datetime.now() - start_time).total_seconds()
        
        # 记录请求完成
        logger.info(f"请求完成: {request.method} {request.url} - {response.status_code} - {process_time:.3f}s")
        
        return response
        
    except Exception as e:
        # 记录请求错误
        process_time = (datetime.now() - start_time).total_seconds()
        logger.error(f"请求错误: {request.method} {request.url} - {str(e)} - {process_time:.3f}s")
        raise

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.server:app",
        host=config.HOST,
        port=config.PORT,
        reload=True,
        log_level="info"
    )