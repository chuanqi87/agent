#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import uuid
from typing import List, Dict, Any, Optional, AsyncGenerator, Union
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import json
import asyncio

from .agent import ChatAgent

# Function Calling 相关数据模型
class FunctionParameter(BaseModel):
    type: str = Field(..., description="参数类型")
    description: Optional[str] = Field(None, description="参数描述")
    enum: Optional[List[str]] = Field(None, description="枚举值")

class FunctionParameters(BaseModel):
    type: str = Field(default="object", description="参数类型")
    properties: Dict[str, FunctionParameter] = Field(..., description="参数属性")
    required: List[str] = Field(default_factory=list, description="必需参数列表")

class Function(BaseModel):
    name: str = Field(..., description="函数名称")
    description: Optional[str] = Field(None, description="函数描述")
    parameters: Optional[FunctionParameters] = Field(None, description="函数参数")

class Tool(BaseModel):
    type: str = Field(default="function", description="工具类型")
    function: Function = Field(..., description="函数定义")

class FunctionCall(BaseModel):
    name: str = Field(..., description="调用的函数名")
    arguments: str = Field(..., description="函数参数JSON字符串")

class ToolCall(BaseModel):
    id: str = Field(..., description="工具调用ID")
    type: str = Field(default="function", description="工具类型")
    function: FunctionCall = Field(..., description="函数调用")

# OpenAI API 兼容的数据模型
class ChatMessage(BaseModel):
    role: str = Field(..., description="消息角色: system, user, assistant, tool")
    content: Optional[str] = Field(None, description="消息内容")
    name: Optional[str] = Field(None, description="消息名称")
    tool_call_id: Optional[str] = Field(None, description="工具调用ID")
    tool_calls: Optional[List[ToolCall]] = Field(None, description="工具调用列表")

class ChatCompletionRequest(BaseModel):
    model: str = Field(default="deepseek-chat", description="模型名称")
    messages: List[ChatMessage] = Field(..., description="对话消息列表")
    temperature: Optional[float] = Field(default=0.7, ge=0, le=2, description="温度参数")
    max_tokens: Optional[int] = Field(default=2000, gt=0, description="最大tokens数")
    stream: Optional[bool] = Field(default=False, description="是否流式返回")
    top_p: Optional[float] = Field(default=1.0, ge=0, le=1, description="top_p参数")
    frequency_penalty: Optional[float] = Field(default=0, ge=-2, le=2, description="频率惩罚")
    presence_penalty: Optional[float] = Field(default=0, ge=-2, le=2, description="存在惩罚")
    user: Optional[str] = Field(default=None, description="用户标识")
    # Function Calling 支持
    functions: Optional[List[Function]] = Field(None, description="可用函数列表(legacy)")
    function_call: Optional[Union[str, Dict[str, str]]] = Field(None, description="函数调用控制(legacy)")
    tools: Optional[List[Tool]] = Field(None, description="可用工具列表")
    tool_choice: Optional[Union[str, Dict[str, Any]]] = Field(None, description="工具选择策略")

class ChatCompletionChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str = "stop"

class ChatCompletionUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: ChatCompletionUsage

# 流式响应的数据模型
class ChatCompletionStreamChoice(BaseModel):
    index: int
    delta: Dict[str, Any]
    finish_reason: Optional[str] = None

class ChatCompletionStreamResponse(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[ChatCompletionStreamChoice]

# 模型信息
class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str = "deepseek"

class ModelsResponse(BaseModel):
    object: str = "list"
    data: List[ModelInfo]

# 创建OpenAI兼容的路由器
openai_router = APIRouter(prefix="/v1")

# 全局agent实例 (将在server.py中初始化)
chat_agent: Optional[ChatAgent] = None

def set_chat_agent(agent: ChatAgent):
    """设置全局chat agent实例"""
    global chat_agent
    chat_agent = agent

@openai_router.get("/models", response_model=ModelsResponse)
async def list_models():
    """获取可用模型列表 (OpenAI兼容)"""
    if not chat_agent:
        raise HTTPException(status_code=500, detail="Chat agent 未初始化")
    
    # 获取当前模型信息
    model_info = chat_agent.get_model_info()
    current_provider = model_info["provider"]
    
    # 根据当前提供商返回相应的模型列表
    models = []
    
    if current_provider == "deepseek":
        models = [
            ModelInfo(
                id="deepseek-chat",
                created=int(time.time()),
                owned_by="deepseek"
            ),
            ModelInfo(
                id="deepseek-reasoner", 
                created=int(time.time()),
                owned_by="deepseek"
            )
        ]
    elif current_provider == "gemini":
        models = [
            ModelInfo(
                id="gemini-2.0-flash-exp",
                created=int(time.time()),
                owned_by="google"
            ),
            ModelInfo(
                id="gemini-1.5-pro",
                created=int(time.time()),
                owned_by="google"
            ),
            ModelInfo(
                id="gemini-1.5-flash",
                created=int(time.time()),
                owned_by="google"
            )
        ]
    elif current_provider == "openai":
        models = [
            ModelInfo(
                id="gpt-4",
                created=int(time.time()),
                owned_by="openai"
            ),
            ModelInfo(
                id="gpt-4-turbo",
                created=int(time.time()),
                owned_by="openai"
            ),
            ModelInfo(
                id="gpt-3.5-turbo",
                created=int(time.time()),
                owned_by="openai"
            )
        ]
    else:
        # 默认返回通用模型列表
        models = [
            ModelInfo(
                id=model_info["model"],
                created=int(time.time()),
                owned_by=current_provider
            )
        ]
    
    return ModelsResponse(data=models)

@openai_router.get("/model/current")
async def get_current_model():
    """获取当前使用的模型信息"""
    if not chat_agent:
        raise HTTPException(status_code=500, detail="Chat agent 未初始化")
    
    model_info = chat_agent.get_model_info()
    memory_stats = chat_agent.get_memory_stats()
    
    return {
        "current_model": model_info,
        "memory_stats": memory_stats,
        "timestamp": int(time.time())
    }

@openai_router.post("/model/switch")
async def switch_model(request: dict):
    """切换模型提供商和模型"""
    if not chat_agent:
        raise HTTPException(status_code=500, detail="Chat agent 未初始化")
    
    provider = request.get("provider")
    api_key = request.get("api_key")
    model = request.get("model")
    
    if not provider:
        raise HTTPException(status_code=400, detail="必须指定模型提供商")
    
    try:
        success = chat_agent.switch_model(provider, api_key, model)
        
        if success:
            new_model_info = chat_agent.get_model_info()
            return {
                "success": True,
                "message": f"成功切换到 {provider.upper()}",
                "new_model": new_model_info
            }
        else:
            raise HTTPException(status_code=500, detail="模型切换失败")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"模型切换错误: {str(e)}")

def estimate_tokens(text: str) -> int:
    """简单的token估算 (1个汉字≈1.5tokens, 1个英文单词≈1token)"""
    chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
    english_words = len([w for w in text.split() if w.isalpha()])
    other_chars = len(text) - chinese_chars - sum(len(w) for w in text.split() if w.isalpha())
    return int(chinese_chars * 1.5 + english_words + other_chars * 0.5)

async def stream_chat_completion(
    request: ChatCompletionRequest,
    completion_id: str
) -> AsyncGenerator[str, None]:
    """流式聊天完成生成器"""
    try:
        # 检查是否包含function calling
        has_functions = bool(request.functions or request.tools)
        
        if has_functions:
            # 对于function calling，暂时不支持流式
            # 因为需要等待模型决定是否调用函数
            yield f"data: {json.dumps({'error': 'Function calling 暂不支持流式模式'})}\n\n"
            return
        
        # 提取最后一条用户消息
        user_message = ""
        for msg in reversed(request.messages):
            if msg.role == "user":
                user_message = msg.content
                break
        
        if not user_message:
            raise HTTPException(status_code=400, detail="没有找到用户消息")
        
        # 调用agent获取完整回复
        full_response = await chat_agent.process_message(user_message)
        
        # 模拟流式返回 (逐字符发送)
        current_content = ""
        
        # 发送开始标记
        start_chunk = ChatCompletionStreamResponse(
            id=completion_id,
            created=int(time.time()),
            model=request.model,
            choices=[ChatCompletionStreamChoice(
                index=0,
                delta={"role": "assistant"},
                finish_reason=None
            )]
        )
        yield f"data: {start_chunk.model_dump_json()}\n\n"
        
        # 逐字符发送内容
        for i, char in enumerate(full_response):
            current_content += char
            
            # 发送每个字符
            delta = {"content": char}
            
            chunk_data = ChatCompletionStreamResponse(
                id=completion_id,
                created=int(time.time()),
                model=request.model,
                choices=[ChatCompletionStreamChoice(
                    index=0,
                    delta=delta,
                    finish_reason=None if i < len(full_response) - 1 else "stop"
                )]
            )
            
            yield f"data: {chunk_data.model_dump_json()}\n\n"
            
            # 在标点符号后稍微延迟，让用户看到打字效果
            if char in '，。！？,.:;!? ':
                await asyncio.sleep(0.1)  # 标点后稍长延迟
            else:
                await asyncio.sleep(0.03)  # 普通字符较短延迟
        
        # 发送结束标记
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        error_chunk = {
            "id": completion_id,
            "object": "chat.completion.chunk", 
            "created": int(time.time()),
            "model": request.model,
            "choices": [{"index": 0, "delta": {}, "finish_reason": "error"}],
            "error": {"message": str(e)}
        }
        yield f"data: {json.dumps(error_chunk)}\n\n"

@openai_router.options("/chat/completions/stream")
async def options_chat_completion_stream():
    """处理CORS预检请求"""
    from fastapi import Response
    response = Response()
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Max-Age"] = "86400"
    return response

@openai_router.post("/chat/completions/stream")
async def create_chat_completion_stream(request: ChatCompletionRequest):
    """专门的SSE流式聊天端点"""
    if not chat_agent:
        raise HTTPException(status_code=500, detail="Chat agent 未初始化")
    
    # 强制启用流式模式
    request.stream = True
    completion_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"
    
    return StreamingResponse(
        stream_chat_completion(request, completion_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "*"
        }
    )

@openai_router.post("/chat/completions")
async def create_chat_completion(request: ChatCompletionRequest):
    """创建聊天完成 (OpenAI兼容，支持Function Calling)"""
    if not chat_agent:
        raise HTTPException(status_code=500, detail="Chat agent 未初始化")
    
    completion_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"
    created_time = int(time.time())
    
    try:
        # 检查是否包含function calling
        has_functions = bool(request.functions or request.tools)
        
        if has_functions:
            print(f"🔧 [Function Calling] 检测到函数调用请求")
            print(f"📋 [Function Calling] 请求数据: {request.model_dump_json(indent=2)}")
            
            # 转换消息格式
            messages = []
            for msg in request.messages:
                message_dict = {"role": msg.role}
                if msg.content:
                    message_dict["content"] = msg.content
                if msg.name:
                    message_dict["name"] = msg.name
                if msg.tool_call_id:
                    message_dict["tool_call_id"] = msg.tool_call_id
                if msg.tool_calls:
                    message_dict["tool_calls"] = [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in msg.tool_calls
                    ]
                messages.append(message_dict)
            
            # 转换functions格式 (legacy支持)
            functions = None
            if request.functions:
                functions = []
                for f in request.functions:
                    func_dict = {
                        "name": f.name,
                        "description": f.description,
                    }
                    
                    # 处理parameters
                    if f.parameters:
                        params = f.parameters.model_dump()
                        # 确保required字段是数组而不是None
                        if "required" in params and params["required"] is None:
                            params["required"] = []
                        
                        # 清理properties中的None值
                        if "properties" in params:
                            cleaned_properties = {}
                            for prop_name, prop_value in params["properties"].items():
                                cleaned_prop = {k: v for k, v in prop_value.items() if v is not None}
                                cleaned_properties[prop_name] = cleaned_prop
                            params["properties"] = cleaned_properties
                        
                        func_dict["parameters"] = params
                    else:
                        func_dict["parameters"] = {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    
                    functions.append(func_dict)
            
            # 转换tools格式
            tools = None
            if request.tools:
                tools = []
                for t in request.tools:
                    tool_dict = {
                        "type": t.type,
                        "function": {
                            "name": t.function.name,
                            "description": t.function.description,
                        }
                    }
                    
                    # 处理parameters
                    if t.function.parameters:
                        params = t.function.parameters.model_dump()
                        # 确保required字段是数组而不是None
                        if "required" in params and params["required"] is None:
                            params["required"] = []
                        
                        # 清理properties中的None值
                        if "properties" in params:
                            cleaned_properties = {}
                            for prop_name, prop_value in params["properties"].items():
                                cleaned_prop = {k: v for k, v in prop_value.items() if v is not None}
                                cleaned_properties[prop_name] = cleaned_prop
                            params["properties"] = cleaned_properties
                        
                        tool_dict["function"]["parameters"] = params
                    else:
                        tool_dict["function"]["parameters"] = {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    
                    tools.append(tool_dict)
            
            # 调用支持function calling的方法
            result = await chat_agent.process_message_with_functions(
                messages=messages,
                functions=functions,
                tools=tools,
                function_call=request.function_call,
                tool_choice=request.tool_choice,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=request.stream
            )
            
            # 转换响应格式
            response_choice = result["choices"][0]
            
            # 构建ChatMessage
            response_message = ChatMessage(
                role=response_choice["message"]["role"],
                content=response_choice["message"].get("content")
            )
            
            # 处理tool_calls
            if "tool_calls" in response_choice["message"]:
                tool_calls = []
                for tc in response_choice["message"]["tool_calls"]:
                    tool_calls.append(ToolCall(
                        id=tc["id"],
                        type=tc["type"],
                        function=FunctionCall(
                            name=tc["function"]["name"],
                            arguments=tc["function"]["arguments"]
                        )
                    ))
                response_message.tool_calls = tool_calls
            
            response = ChatCompletionResponse(
                id=completion_id,
                created=created_time,
                model=request.model,
                choices=[ChatCompletionChoice(
                    index=0,
                    message=response_message,
                    finish_reason=response_choice.get("finish_reason", "stop")
                )],
                usage=ChatCompletionUsage(
                    prompt_tokens=result["usage"]["prompt_tokens"],
                    completion_tokens=result["usage"]["completion_tokens"],
                    total_tokens=result["usage"]["total_tokens"]
                )
            )
            
            print(f"✅ [Function Calling] 返回响应")
            return response
        
        # 普通聊天处理逻辑
        # 提取最后一条用户消息
        user_message = ""
        for msg in reversed(request.messages):
            if msg.role == "user":
                user_message = msg.content
                break
        
        if not user_message:
            raise HTTPException(status_code=400, detail="没有找到用户消息")
        
        print(f"🔥 [OpenAI API] 收到聊天请求: {user_message[:50]}...")
        
        # 如果是流式请求
        if request.stream:
            return StreamingResponse(
                stream_chat_completion(request, completion_id),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "text/event-stream",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Allow-Methods": "*"
                }
            )
        
        # 非流式请求：调用LangChain agent
        ai_response = await chat_agent.process_message(user_message)
        
        # 计算token使用量
        prompt_text = " ".join([msg.content or "" for msg in request.messages])
        prompt_tokens = estimate_tokens(prompt_text)
        completion_tokens = estimate_tokens(ai_response)
        total_tokens = prompt_tokens + completion_tokens
        
        response = ChatCompletionResponse(
            id=completion_id,
            created=created_time,
            model=request.model,
            choices=[ChatCompletionChoice(
                index=0,
                message=ChatMessage(role="assistant", content=ai_response),
                finish_reason="stop"
            )],
            usage=ChatCompletionUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens
            )
        )
        
        print(f"✅ [OpenAI API] 返回回复: {ai_response[:50]}...")
        return response
        
    except Exception as e:
        print(f"❌ [OpenAI API] 处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理请求时出错: {str(e)}")

# 兼容性端点
@openai_router.get("/")
async def openai_root():
    """OpenAI API 根端点"""
    return {
        "message": "OpenAI Compatible API",
        "service": "AI Agent Backend", 
        "version": "0.1.0",
        "framework": "LangChain + DeepSeek"
    } 