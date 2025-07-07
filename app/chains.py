from typing import Dict, Any, List, Optional, AsyncGenerator
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain.schema.runnable import Runnable, RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain.callbacks.base import BaseCallbackHandler
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
import json
import asyncio
import uuid
from datetime import datetime

from .config import config
from .tools import tool_manager
from .models import Message, Role, ToolCall, ChatCompletionRequest

class StreamingCallbackHandler(BaseCallbackHandler):
    """流式回调处理器"""
    
    def __init__(self):
        self.tokens = []
        self.current_token = ""
    
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """处理新的token"""
        self.tokens.append(token)
        self.current_token = token
    
    def get_tokens(self) -> List[str]:
        """获取所有token"""
        return self.tokens
    
    def clear(self):
        """清空token"""
        self.tokens = []
        self.current_token = ""

class AgentChain:
    """Agent链管理器"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=config.DEFAULT_MODEL,
            temperature=config.TEMPERATURE,
            max_tokens=config.MAX_TOKENS,
            openai_api_key=config.OPENAI_API_KEY,
            openai_api_base=config.OPENAI_BASE_URL,
            streaming=True
        )
        
        # 创建系统提示
        self.system_prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个智能助手，具有工具调用能力。你可以使用以下工具来帮助用户：

可用工具：
{tools}

请根据用户的需求选择合适的工具。如果需要使用工具，请按照工具的描述正确调用。
如果不需要使用工具，请直接回答用户的问题。

记住：
1. 始终以用户的需求为中心
2. 如果不确定如何回答，可以要求用户提供更多信息
3. 使用工具时要确保参数正确
4. 提供清晰、有用的回答
"""),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        # 获取工具列表
        self.tools = tool_manager.get_all_tools()
        
        # 创建agent
        if config.ENABLE_TOOLS and self.tools:
            self.agent = create_openai_tools_agent(
                self.llm,
                self.tools,
                self.system_prompt
            )
            self.agent_executor = AgentExecutor(
                agent=self.agent,
                tools=self.tools,
                verbose=True,
                handle_parsing_errors=True
            )
        else:
            self.agent = None
            self.agent_executor = None
    
    def _convert_messages(self, messages: List[Message]) -> List[BaseMessage]:
        """转换消息格式"""
        converted = []
        for msg in messages:
            if msg.role == Role.SYSTEM:
                converted.append(SystemMessage(content=msg.content or ""))
            elif msg.role == Role.USER:
                converted.append(HumanMessage(content=msg.content or ""))
            elif msg.role == Role.ASSISTANT:
                converted.append(AIMessage(content=msg.content or ""))
        return converted
    
    def _format_tools_description(self) -> str:
        """格式化工具描述"""
        if not self.tools:
            return "暂无可用工具"
        
        descriptions = []
        for tool in self.tools:
            descriptions.append(f"- {tool.name}: {tool.description}")
        
        return "\n".join(descriptions)
    
    async def process_request(self, request: ChatCompletionRequest) -> AsyncGenerator[str, None]:
        """处理聊天请求"""
        try:
            # 转换消息格式
            messages = self._convert_messages(request.messages)
            
            # 检查是否需要工具调用
            if (config.ENABLE_TOOLS and 
                request.tools and 
                self.agent_executor):
                
                # 使用agent executor处理工具调用
                async for chunk in self._process_with_tools(messages, request):
                    yield chunk
            else:
                # 直接使用LLM处理
                async for chunk in self._process_direct(messages, request):
                    yield chunk
                    
        except Exception as e:
            error_msg = f"处理请求时发生错误: {str(e)}"
            yield json.dumps({
                "error": {
                    "message": error_msg,
                    "type": "processing_error"
                }
            })
    
    async def _process_with_tools(self, messages: List[BaseMessage], request: ChatCompletionRequest) -> AsyncGenerator[str, None]:
        """使用工具处理请求"""
        try:
            # 准备输入
            input_data = {
                "messages": messages,
                "tools": self._format_tools_description()
            }
            
            # 创建流式回调
            callback = StreamingCallbackHandler()
            
            # 异步执行agent
            result = await self.agent_executor.ainvoke(
                input_data,
                callbacks=[callback]
            )
            
            # 处理结果
            if isinstance(result, dict) and "output" in result:
                content = result["output"]
                
                # 模拟流式输出
                words = content.split()
                for i, word in enumerate(words):
                    chunk_data = {
                        "id": f"chatcmpl-{uuid.uuid4().hex[:29]}",
                        "object": "chat.completion.chunk",
                        "created": int(datetime.now().timestamp()),
                        "model": request.model,
                        "choices": [{
                            "index": 0,
                            "delta": {
                                "content": word + " " if i < len(words) - 1 else word
                            },
                            "finish_reason": None
                        }]
                    }
                    
                    yield f"data: {json.dumps(chunk_data)}\n\n"
                    await asyncio.sleep(0.01)  # 模拟延迟
                
                # 发送结束标记
                final_chunk = {
                    "id": f"chatcmpl-{uuid.uuid4().hex[:29]}",
                    "object": "chat.completion.chunk",
                    "created": int(datetime.now().timestamp()),
                    "model": request.model,
                    "choices": [{
                        "index": 0,
                        "delta": {},
                        "finish_reason": "stop"
                    }]
                }
                
                yield f"data: {json.dumps(final_chunk)}\n\n"
                yield "data: [DONE]\n\n"
            
        except Exception as e:
            error_msg = f"工具处理错误: {str(e)}"
            yield json.dumps({
                "error": {
                    "message": error_msg,
                    "type": "tool_error"
                }
            })
    
    async def _process_direct(self, messages: List[BaseMessage], request: ChatCompletionRequest) -> AsyncGenerator[str, None]:
        """直接处理请求"""
        try:
            # 创建链
            chain = self.system_prompt | self.llm | StrOutputParser()
            
            # 准备输入
            input_data = {
                "messages": messages,
                "tools": self._format_tools_description()
            }
            
            # 异步流式处理
            async for chunk in chain.astream(input_data):
                if chunk:
                    chunk_data = {
                        "id": f"chatcmpl-{uuid.uuid4().hex[:29]}",
                        "object": "chat.completion.chunk",
                        "created": int(datetime.now().timestamp()),
                        "model": request.model,
                        "choices": [{
                            "index": 0,
                            "delta": {
                                "content": chunk
                            },
                            "finish_reason": None
                        }]
                    }
                    
                    yield f"data: {json.dumps(chunk_data)}\n\n"
            
            # 发送结束标记
            final_chunk = {
                "id": f"chatcmpl-{uuid.uuid4().hex[:29]}",
                "object": "chat.completion.chunk",
                "created": int(datetime.now().timestamp()),
                "model": request.model,
                "choices": [{
                    "index": 0,
                    "delta": {},
                    "finish_reason": "stop"
                }]
            }
            
            yield f"data: {json.dumps(final_chunk)}\n\n"
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            error_msg = f"直接处理错误: {str(e)}"
            yield json.dumps({
                "error": {
                    "message": error_msg,
                    "type": "direct_error"
                }
            })
    
    async def process_non_streaming(self, request: ChatCompletionRequest) -> Dict[str, Any]:
        """处理非流式请求"""
        try:
            # 转换消息格式
            messages = self._convert_messages(request.messages)
            
            # 准备输入
            input_data = {
                "messages": messages,
                "tools": self._format_tools_description()
            }
            
            if (config.ENABLE_TOOLS and 
                request.tools and 
                self.agent_executor):
                
                # 使用agent executor
                result = await self.agent_executor.ainvoke(input_data)
                content = result.get("output", "")
            else:
                # 直接使用LLM
                chain = self.system_prompt | self.llm | StrOutputParser()
                content = await chain.ainvoke(input_data)
            
            # 构造响应
            response = {
                "id": f"chatcmpl-{uuid.uuid4().hex[:29]}",
                "object": "chat.completion",
                "created": int(datetime.now().timestamp()),
                "model": request.model,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": content
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": 0,  # 简化处理
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
            }
            
            return response
            
        except Exception as e:
            return {
                "error": {
                    "message": f"处理请求时发生错误: {str(e)}",
                    "type": "processing_error"
                }
            }

# 全局agent链实例
agent_chain = AgentChain()