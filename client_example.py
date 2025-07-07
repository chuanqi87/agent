#!/usr/bin/env python3
"""
LangServe Agent Backend 客户端使用示例
演示如何使用OpenAI兼容的API接口
"""

import asyncio
import httpx
import json
from typing import Dict, Any, List

class AgentClient:
    """Agent客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        response = await self.client.get(f"{self.base_url}/health")
        return response.json()
    
    async def list_models(self) -> Dict[str, Any]:
        """列出可用模型"""
        response = await self.client.get(f"{self.base_url}/v1/models")
        return response.json()
    
    async def list_tools(self) -> Dict[str, Any]:
        """列出可用工具"""
        response = await self.client.get(f"{self.base_url}/v1/tools")
        return response.json()
    
    async def chat_completion(self, 
                            messages: List[Dict[str, str]], 
                            model: str = "gpt-3.5-turbo",
                            stream: bool = False,
                            tools: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """聊天完成"""
        data = {
            "model": model,
            "messages": messages,
            "stream": stream
        }
        
        if tools:
            data["tools"] = tools
        
        if stream:
            # 流式响应
            async with self.client.stream(
                "POST", 
                f"{self.base_url}/v1/chat/completions",
                json=data,
                headers={"Content-Type": "application/json"}
            ) as response:
                async for chunk in response.aiter_text():
                    if chunk.strip():
                        # 解析SSE数据
                        for line in chunk.strip().split('\n'):
                            if line.startswith('data: '):
                                data_str = line[6:]  # 去掉 'data: ' 前缀
                                if data_str == '[DONE]':
                                    break
                                try:
                                    yield json.loads(data_str)
                                except json.JSONDecodeError:
                                    continue
        else:
            # 非流式响应
            response = await self.client.post(
                f"{self.base_url}/v1/chat/completions",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            return response.json()
    
    async def execute_tool(self, tool_name: str, arguments: str) -> Dict[str, Any]:
        """执行工具"""
        data = {
            "tool_name": tool_name,
            "arguments": arguments
        }
        
        response = await self.client.post(
            f"{self.base_url}/v1/tools/execute",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        return response.json()
    
    async def get_agent_info(self) -> Dict[str, Any]:
        """获取Agent信息"""
        response = await self.client.get(f"{self.base_url}/v1/agent/info")
        return response.json()
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()

async def main():
    """主函数，演示API使用"""
    client = AgentClient()
    
    try:
        print("=== LangServe Agent Backend 客户端示例 ===\n")
        
        # 1. 健康检查
        print("1. 健康检查:")
        health = await client.health_check()
        print(json.dumps(health, indent=2, ensure_ascii=False))
        print()
        
        # 2. 获取Agent信息
        print("2. Agent信息:")
        agent_info = await client.get_agent_info()
        print(json.dumps(agent_info, indent=2, ensure_ascii=False))
        print()
        
        # 3. 列出可用模型
        print("3. 可用模型:")
        models = await client.list_models()
        print(json.dumps(models, indent=2, ensure_ascii=False))
        print()
        
        # 4. 列出可用工具
        print("4. 可用工具:")
        tools = await client.list_tools()
        print(json.dumps(tools, indent=2, ensure_ascii=False))
        print()
        
        # 5. 简单聊天（非流式）
        print("5. 简单聊天（非流式）:")
        messages = [
            {"role": "user", "content": "你好！你是谁？"}
        ]
        
        response = await client.chat_completion(messages, stream=False)
        print(json.dumps(response, indent=2, ensure_ascii=False))
        print()
        
        # 6. 流式聊天
        print("6. 流式聊天:")
        messages = [
            {"role": "user", "content": "请用中文介绍一下你的能力"}
        ]
        
        print("回复：", end="")
        async for chunk in client.chat_completion(messages, stream=True):
            if 'choices' in chunk and chunk['choices']:
                delta = chunk['choices'][0].get('delta', {})
                if 'content' in delta:
                    print(delta['content'], end="", flush=True)
        print("\n")
        
        # 7. 工具调用示例
        print("7. 工具调用示例:")
        
        # 计算器工具
        print("计算器工具:")
        calc_result = await client.execute_tool("calculator", "2 + 3 * 4")
        print(json.dumps(calc_result, indent=2, ensure_ascii=False))
        
        # 时间工具
        print("时间工具:")
        time_result = await client.execute_tool("current_time", "")
        print(json.dumps(time_result, indent=2, ensure_ascii=False))
        print()
        
        # 8. 带工具的聊天
        print("8. 带工具的聊天:")
        messages = [
            {"role": "user", "content": "请帮我计算 15 * 23 + 45，然后告诉我现在的时间"}
        ]
        
        # 获取工具定义
        tools_response = await client.list_tools()
        tools_list = tools_response.get("tools", [])
        
        print("回复：", end="")
        async for chunk in client.chat_completion(messages, stream=True, tools=tools_list):
            if 'choices' in chunk and chunk['choices']:
                delta = chunk['choices'][0].get('delta', {})
                if 'content' in delta:
                    print(delta['content'], end="", flush=True)
        print("\n")
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
    
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())