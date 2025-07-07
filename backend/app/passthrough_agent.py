#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import httpx
from typing import Dict, Any, List, Optional
import time
import uuid
from .config import get_settings

class DirectAgent:
    """直接透传的Agent"""
    
    def __init__(self):
        settings = get_settings()
        self.model_config = settings.get_active_model_config()
        self.client = httpx.AsyncClient(timeout=120.0)
        print(f"✅ DirectAgent初始化完成")
        
    async def stream_chat(self, messages: List[Dict], tools: Optional[List[Dict]] = None, **kwargs):
        """流式聊天，直接透传给大模型"""
        request_id = str(uuid.uuid4())[:8]
        
        print(f"\n🔄 [{request_id}] 开始流式聊天请求")
        print(f"📝 [{request_id}] 消息数量: {len(messages)}")
        print(f"🔧 [{request_id}] 工具数量: {len(tools) if tools else 0}")
        
        # 构建请求数据
        request_data = {
            "model": self.model_config["model"],
            "messages": messages,
            "stream": True,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2000),
        }
        
        # 如果有tools，也透传
        if tools:
            request_data["tools"] = tools
            request_data["tool_choice"] = kwargs.get("tool_choice", "auto")
            print(f"🔧 [{request_id}] 工具配置: {request_data['tool_choice']}")
        
        # 添加其他参数
        for key, value in kwargs.items():
            if key not in ["temperature", "max_tokens", "tool_choice"]:
                request_data[key] = value
                print(f"⚙️  [{request_id}] 额外参数: {key}={value}")
        
        # 打印最后一条用户消息（用于调试）
        if messages:
            last_message = messages[-1]
            print(f"💬 [{request_id}] 最后消息: {last_message.get('role', 'unknown')} - {last_message.get('content', '')[:100]}...")
        
        # 构建请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.model_config['api_key']}",
        }
        
        print(f"🌐 [{request_id}] 发送请求到: {self.model_config['base_url']}/chat/completions")
        print(f"📊 [{request_id}] 请求参数: model={request_data['model']}, stream={request_data['stream']}")
        
        try:
            start_time = time.time()
            
            # 发送请求并流式返回
            async with self.client.stream(
                "POST",
                f"{self.model_config['base_url']}/chat/completions",
                json=request_data,
                headers=headers
            ) as response:
                response_time = time.time() - start_time
                print(f"⏱️  [{request_id}] 连接建立耗时: {response_time:.2f}s")
                print(f"📈 [{request_id}] 响应状态码: {response.status_code}")
                
                if response.status_code != 200:
                    error_text = await response.aread()
                    print(f"❌ [{request_id}] API请求失败: {response.status_code}")
                    print(f"❌ [{request_id}] 错误内容: {error_text.decode()}")
                    raise Exception(f"API请求失败: {response.status_code} - {error_text.decode()}")
                
                chunk_count = 0
                valid_chunk_count = 0
                
                async for raw_chunk in response.aiter_text():
                    if raw_chunk.strip():
                        chunk_count += 1
                        
                        # 处理每一行数据
                        for line in raw_chunk.strip().split('\n'):
                            line = line.strip()
                            if line.startswith('data: '):
                                data = line[6:].strip()
                                
                                if data == '[DONE]':
                                    print(f"✅ [{request_id}] 流式响应完成，共处理 {chunk_count} 个原始chunk，{valid_chunk_count} 个有效chunk")
                                    yield "data: [DONE]\n\n"
                                    return
                                elif data:
                                    # 验证JSON格式
                                    try:
                                        json.loads(data)
                                        valid_chunk_count += 1
                                        # 每100个有效chunk打印一次进度
                                        if valid_chunk_count % 100 == 0:
                                            print(f"📡 [{request_id}] 已处理 {valid_chunk_count} 个有效chunk")
                                        # 直接转发数据
                                        yield f"data: {data}\n\n"
                                    except json.JSONDecodeError:
                                        # 如果JSON格式错误，记录日志但不转发
                                        if chunk_count % 100 == 0:  # 减少错误日志频率
                                            print(f"⚠️  [{request_id}] 跳过无效JSON数据 (第{chunk_count}个chunk)")
                                        continue
                
        except Exception as e:
            print(f"❌ [{request_id}] 流式请求异常: {str(e)}")
            raise e
    
    async def chat(self, messages: List[Dict], tools: Optional[List[Dict]] = None, **kwargs):
        """非流式聊天，直接透传给大模型"""
        request_id = str(uuid.uuid4())[:8]
        
        print(f"\n🔄 [{request_id}] 开始非流式聊天请求")
        print(f"📝 [{request_id}] 消息数量: {len(messages)}")
        print(f"🔧 [{request_id}] 工具数量: {len(tools) if tools else 0}")
        
        # 构建请求数据
        request_data = {
            "model": self.model_config["model"],
            "messages": messages,
            "stream": False,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2000),
        }
        
        # 如果有tools，也透传
        if tools:
            request_data["tools"] = tools
            request_data["tool_choice"] = kwargs.get("tool_choice", "auto")
            print(f"🔧 [{request_id}] 工具配置: {request_data['tool_choice']}")
        
        # 添加其他参数
        for key, value in kwargs.items():
            if key not in ["temperature", "max_tokens", "tool_choice"]:
                request_data[key] = value
                print(f"⚙️  [{request_id}] 额外参数: {key}={value}")
        
        # 打印最后一条用户消息（用于调试）
        if messages:
            last_message = messages[-1]
            print(f"💬 [{request_id}] 最后消息: {last_message.get('role', 'unknown')} - {last_message.get('content', '')[:100]}...")
        
        # 构建请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.model_config['api_key']}",
        }
        
        print(f"🌐 [{request_id}] 发送请求到: {self.model_config['base_url']}/chat/completions")
        print(f"📊 [{request_id}] 请求参数: model={request_data['model']}, stream={request_data['stream']}")
        
        try:
            start_time = time.time()
            
            # 发送请求
            response = await self.client.post(
                f"{self.model_config['base_url']}/chat/completions",
                json=request_data,
                headers=headers
            )
            
            response_time = time.time() - start_time
            print(f"⏱️  [{request_id}] 请求耗时: {response_time:.2f}s")
            print(f"📈 [{request_id}] 响应状态码: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ [{request_id}] API请求失败: {response.status_code}")
                print(f"❌ [{request_id}] 错误内容: {response.text}")
                raise Exception(f"API请求失败: {response.status_code} - {response.text}")
            
            result = response.json()
            
            # 打印响应摘要
            if "choices" in result and len(result["choices"]) > 0:
                choice = result["choices"][0]
                if "message" in choice:
                    content = choice["message"].get("content", "")
                    print(f"✅ [{request_id}] 响应内容长度: {len(content)} 字符")
                    print(f"✅ [{request_id}] 响应预览: {content[:100]}...")
                    
                if "tool_calls" in choice.get("message", {}):
                    tool_calls = choice["message"]["tool_calls"]
                    print(f"🔧 [{request_id}] 工具调用数量: {len(tool_calls)}")
                    for i, tool_call in enumerate(tool_calls):
                        print(f"🔧 [{request_id}] 工具{i+1}: {tool_call.get('function', {}).get('name', 'unknown')}")
            
            return result
            
        except Exception as e:
            print(f"❌ [{request_id}] 非流式请求异常: {str(e)}")
            raise e
    
    def get_model_info(self):
        """获取模型信息"""
        return {
            "provider": self.model_config["provider"],
            "model": self.model_config["model"],
            "base_url": self.model_config["base_url"]
        }
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()
        print("🔒 DirectAgent HTTP客户端已关闭") 