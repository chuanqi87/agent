#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from typing import List, Dict, Any, Optional, Union
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.chains import ConversationChain
from langchain.prompts import (
    ChatPromptTemplate, 
    MessagesPlaceholder, 
    SystemMessagePromptTemplate, 
    HumanMessagePromptTemplate
)
from fastapi import HTTPException
from .config import get_settings

class ChatAgent:
    """基于LangChain的聊天代理，支持Function Calling和多模型切换"""
    
    def __init__(self):
        """初始化聊天代理"""
        self.settings = get_settings()
        self.model_config = self.settings.get_active_model_config()
        self.setup_llm()
        self.setup_memory()
        self.setup_prompt_template()
        self.setup_conversation_chain()
    
    def setup_llm(self):
        """设置LangChain LLM，支持多种模型"""
        if not self.model_config["api_key"]:
            raise ValueError(f"请在.env文件中设置{self.model_config['provider'].upper()}_API_KEY")
        
        # 根据模型提供商调整配置
        provider = self.model_config["provider"]
        model_name = self.model_config["model"]
        
        # 对于Gemini，需要特殊处理
        if provider == "gemini":
            # Gemini通过OpenAI兼容接口访问
            base_url = self.model_config["base_url"]
            # 如果使用Google AI Studio的API
            if "generativelanguage.googleapis.com" in base_url:
                # 构建兼容的URL
                base_url = f"{base_url}/openai"
        else:
            base_url = self.model_config["base_url"]
        
        self.llm = ChatOpenAI(
            openai_api_key=self.model_config["api_key"],
            openai_api_base=base_url,
            model_name=model_name,
            temperature=0.7,
            max_tokens=2000,
            streaming=False
        )
        
        print(f"✅ LangChain + {provider.upper()} LLM 初始化成功")
        print(f"📡 Base URL: {base_url}")
        print(f"🤖 Model: {model_name}")
    
    def setup_memory(self):
        """设置对话记忆"""
        self.memory = ConversationBufferWindowMemory(
            k=10,  # 保留最近10轮对话
            return_messages=True,
            memory_key="chat_history"
        )
        print(f"🧠 对话记忆初始化成功 (窗口大小: {self.memory.k})")
    
    def setup_prompt_template(self):
        """设置提示模板"""
        provider = self.model_config["provider"]
        model_name = self.model_config["model"]
        
        system_message = f"""你是一个医生。请遵循以下原则：

1. 用中文回答问题
2. 保持友好和专业的语调  
3. 如果不确定答案，请诚实说明
4. 尽量提供有用和准确的信息
5. 可以进行多轮对话，记住之前的上下文
6. 展现出深度思考和推理能力
7. 利用LangChain的能力提供更智能的回答
8. 如果有可用的工具函数，请合理使用它们来帮助用户

请根据用户的问题提供最好的帮助。"""
        
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_message),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{input}")
        ])
        print(f"📝 提示模板设置完成 - {provider}")
    
    def setup_conversation_chain(self):
        """设置对话链"""
        self.conversation = ConversationChain(
            llm=self.llm,
            prompt=self.prompt,
            memory=self.memory,
            verbose=True  # 启用详细日志
        )
        print(f"🔗 对话链初始化完成")
    
    def switch_model(self, provider: str, api_key: str = None, model: str = None):
        """动态切换模型"""
        try:
            # 更新配置
            if provider.lower() == "deepseek":
                if api_key:
                    self.settings.DEEPSEEK_API_KEY = api_key
                if model:
                    self.settings.DEEPSEEK_MODEL = model
                self.settings.MODEL_PROVIDER = "deepseek"
            elif provider.lower() == "gemini":
                if api_key:
                    self.settings.GEMINI_API_KEY = api_key
                if model:
                    self.settings.GEMINI_MODEL = model
                self.settings.MODEL_PROVIDER = "gemini"
            elif provider.lower() == "openai":
                if api_key:
                    self.settings.OPENAI_API_KEY_ORIGINAL = api_key
                if model:
                    self.settings.OPENAI_MODEL_ORIGINAL = model
                self.settings.MODEL_PROVIDER = "openai"
            
            # 重新初始化
            self.model_config = self.settings.get_active_model_config()
            self.setup_llm()
            self.setup_prompt_template()
            self.setup_conversation_chain()
            
            print(f"✅ 成功切换到 {provider.upper()} 模型")
            return True
            
        except Exception as e:
            print(f"❌ 模型切换失败: {str(e)}")
            return False
    
    async def process_message(self, user_message: str, **kwargs) -> str:
        """使用LangChain处理用户消息并返回AI回复"""
        try:
            print(f"📤 [LangChain {self.model_config['provider'].upper()}] 处理用户消息: {user_message[:50]}...")
            
            # 使用LangChain对话链处理消息
            response = await self.llm.ainvoke(
                self.prompt.format_messages(
                    chat_history=self.memory.chat_memory.messages,
                    input=user_message
                )
            )
            
            ai_response = response.content
            print(f"📥 [LangChain {self.model_config['provider'].upper()}] 收到回复: {ai_response[:50]}...")
            
            # 更新LangChain记忆
            self.memory.chat_memory.add_user_message(user_message)
            self.memory.chat_memory.add_ai_message(ai_response)
            
            return ai_response
            
        except Exception as e:
            error_msg = f"❌ LangChain + {self.model_config['provider'].upper()} 处理失败: {str(e)}"
            print(error_msg)
            return f"抱歉，处理您的消息时出现了错误：{str(e)}"
    
    async def process_message_with_functions(
        self, 
        messages: List[Dict[str, Any]], 
        functions: Optional[List[Dict[str, Any]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        function_call: Optional[Union[str, Dict[str, str]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """处理带有function calling的消息"""
        try:
            provider = self.model_config["provider"]
            print(f"🔧 [Function Calling {provider.upper()}] 处理消息 - Functions: {len(functions or [])}, Tools: {len(tools or [])}")
            
            # 构建发送给底层模型的请求
            request_data = {
                "model": self.model_config["model"],
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 2000),
                "stream": kwargs.get("stream", False)
            }
            
            # 添加function calling相关参数
            if functions:
                request_data["functions"] = functions
                if function_call:
                    request_data["function_call"] = function_call
            
            if tools:
                request_data["tools"] = tools
                if tool_choice:
                    request_data["tool_choice"] = tool_choice
                    
            # 根据不同提供商调整API调用
            import httpx
            
            headers = {
                "Authorization": f"Bearer {self.model_config['api_key']}",
                "Content-Type": "application/json"
            }
            
            # 构建API端点
            base_url = self.model_config["base_url"]
            if provider == "gemini" and "generativelanguage.googleapis.com" in base_url:
                # 对于Google AI Studio，使用OpenAI兼容格式
                api_url = f"{base_url}/openai/chat/completions"
            else:
                api_url = f"{base_url}/chat/completions"
            
            # 发送请求到底层模型API
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    api_url,
                    headers=headers,
                    json=request_data,
                    timeout=60.0
                )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"底层{provider.upper()}API调用失败: {response.text}"
                    )
                
                result = response.json()
                print(f"✅ [Function Calling {provider.upper()}] 底层模型响应成功")
                
                return result
                
        except Exception as e:
            error_msg = f"❌ Function Calling {self.model_config['provider'].upper()} 处理失败: {str(e)}"
            print(error_msg)
            raise e
    
    async def process_message_with_chain(self, user_message: str) -> str:
        """使用对话链处理消息 (同步转异步包装)"""
        try:
            provider = self.model_config["provider"]
            print(f"📤 [Chain {provider.upper()}] 处理用户消息: {user_message[:50]}...")
            
            # 直接使用对话链 (LangChain自动管理一切)
            import asyncio
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                self.conversation.predict,
                user_message
            )
            
            print(f"📥 [Chain {provider.upper()}] 收到回复: {response[:50]}...")
            return response
            
        except Exception as e:
            error_msg = f"❌ LangChain Chain {self.model_config['provider'].upper()} 处理失败: {str(e)}"
            print(error_msg)
            return f"抱歉，处理您的消息时出现了错误：{str(e)}"
    
    def clear_history(self):
        """清除LangChain对话历史"""
        self.memory.clear()
        print("✅ LangChain对话历史已清除")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """获取记忆统计信息"""
        messages = self.memory.chat_memory.messages
        return {
            "total_messages": len(messages),
            "user_messages": len([m for m in messages if m.type == "human"]),
            "ai_messages": len([m for m in messages if m.type == "ai"]),
            "memory_window": self.memory.k,
            "current_model": self.model_config["model"],
            "current_provider": self.model_config["provider"]
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取当前模型信息"""
        return {
            "provider": self.model_config["provider"],
            "model": self.model_config["model"],
            "base_url": self.model_config["base_url"],
            "has_api_key": bool(self.model_config["api_key"])
        }
    
    async def get_conversation_summary(self) -> str:
        """获取对话摘要 (使用LangChain)"""
        try:
            messages = self.memory.chat_memory.messages
            if not messages:
                return "暂无对话历史"
            
            # 构建摘要提示
            conversation_text = "\n".join([
                f"{'用户' if m.type == 'human' else 'AI'}: {m.content}"
                for m in messages[-10:]  # 最近10条消息
            ])
            
            summary_prompt = f"""请为以下对话生成一个简洁的摘要：

{conversation_text}

摘要："""
            
            response = await self.llm.ainvoke([HumanMessage(content=summary_prompt)])
            return response.content
            
        except Exception as e:
            return f"生成摘要失败: {str(e)}" 