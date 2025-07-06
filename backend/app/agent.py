#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda
from langchain_core.tools import tool
from langchain.memory import ConversationBufferWindowMemory
from langchain.agents import AgentExecutor, create_openai_tools_agent
from .config import get_settings
from .tools import TOOLS

class ChatAgent:
    """基于LangChain和langserve的聊天代理"""
    
    def __init__(self):
        """初始化聊天代理"""
        self.settings = get_settings()
        self.model_config = self.settings.get_active_model_config()
        self.setup_llm()
        self.setup_tools()
        self.setup_agent()
        self.setup_memory()
        
    def setup_llm(self):
        """设置LangChain LLM"""
        if not self.model_config["api_key"]:
            raise ValueError(f"请在.env文件中设置{self.model_config['provider'].upper()}_API_KEY")
        
        provider = self.model_config["provider"]
        model_name = self.model_config["model"]
        base_url = self.model_config["base_url"]
        
        # 对于Gemini，需要特殊处理
        if provider == "gemini":
            if "generativelanguage.googleapis.com" in base_url:
                base_url = f"{base_url}/openai"
        
        self.llm = ChatOpenAI(
            openai_api_key=self.model_config["api_key"],
            openai_api_base=base_url,
            model_name=model_name,
            temperature=0.7,
            max_tokens=2000,
            streaming=True  # 支持流式响应
        )
        
        print(f"✅ LangChain LLM 初始化成功 - {provider.upper()} {model_name}")
    
    def setup_tools(self):
        """设置工具"""
        self.tools = TOOLS
        print(f"🔧 工具初始化完成 - {len(self.tools)} 个工具")
    
    def setup_agent(self):
        """设置Agent"""
        # 创建系统提示
        system_prompt = """你是一个智能助手。请遵循以下原则：

1. 用中文回答问题
2. 保持友好和专业的语调
3. 如果不确定答案，请诚实说明
4. 合理使用可用的工具来帮助用户
5. 展现深度思考和推理能力

请根据用户的需求选择合适的工具。"""
        
        # 创建提示模板
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # 创建OpenAI工具代理
        self.agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # 创建代理执行器
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3
        )
        
        print("🤖 Agent 初始化完成")
    
    def setup_memory(self):
        """设置记忆"""
        self.memory = ConversationBufferWindowMemory(
            k=10,  # 保留最近10轮对话
            return_messages=True,
            memory_key="chat_history"
        )
        print("🧠 记忆系统初始化完成")
    
    def get_chain(self):
        """获取可用于langserve的链"""
        def format_input(input_data):
            """格式化输入"""
            if isinstance(input_data, dict):
                user_input = input_data.get("input", "")
            else:
                user_input = str(input_data)
            
            # 获取聊天历史
            chat_history = self.memory.chat_memory.messages
            
            return {
                "input": user_input,
                "chat_history": chat_history,
                "agent_scratchpad": []
            }
        
        def save_to_memory(result):
            """保存到记忆"""
            input_msg = result.get("input", "")
            output_msg = result.get("output", "")
            
            if input_msg and output_msg:
                self.memory.chat_memory.add_user_message(input_msg)
                self.memory.chat_memory.add_ai_message(output_msg)
            
            return result
        
        # 创建链
        chain = (
            RunnableLambda(format_input) |
            self.agent_executor |
            RunnableLambda(save_to_memory)
        )
        
        return chain
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "provider": self.model_config["provider"],
            "model": self.model_config["model"],
            "base_url": self.model_config["base_url"],
            "tools_count": len(self.tools),
            "tools": [tool.name for tool in self.tools]
        } 