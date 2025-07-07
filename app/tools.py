from typing import Dict, Any, List, Optional, Callable
from langchain.tools import BaseTool
from langchain.schema import AgentAction, AgentFinish
from pydantic import BaseModel, Field
import json
import requests
import datetime

class CalculatorTool(BaseTool):
    """简单的计算器工具"""
    name = "calculator"
    description = "用于执行数学计算的工具。输入应该是有效的数学表达式。"
    
    def _run(self, query: str) -> str:
        """执行数学计算"""
        try:
            # 简单的安全检查
            if any(x in query.lower() for x in ['import', 'exec', 'eval', '__', 'open', 'file']):
                return "错误：包含不安全的操作"
            
            # 只允许基本的数学运算
            allowed_chars = set('0123456789+-*/.() ')
            if not all(c in allowed_chars for c in query):
                return "错误：包含不允许的字符"
            
            result = eval(query)
            return str(result)
        except Exception as e:
            return f"计算错误: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        """异步执行"""
        return self._run(query)

class CurrentTimeTool(BaseTool):
    """获取当前时间的工具"""
    name = "current_time"
    description = "获取当前的日期和时间"
    
    def _run(self, query: str = "") -> str:
        """获取当前时间"""
        now = datetime.datetime.now()
        return f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}"
    
    async def _arun(self, query: str = "") -> str:
        """异步执行"""
        return self._run(query)

class WeatherTool(BaseTool):
    """天气查询工具（示例）"""
    name = "weather"
    description = "查询指定城市的天气信息。输入应该是城市名称。"
    
    def _run(self, city: str) -> str:
        """查询天气"""
        try:
            # 这里是一个模拟的天气API调用
            # 在实际应用中，你需要替换为真实的天气API
            return f"城市 {city} 的天气：晴朗，温度 22°C，湿度 65%"
        except Exception as e:
            return f"天气查询失败: {str(e)}"
    
    async def _arun(self, city: str) -> str:
        """异步执行"""
        return self._run(city)

class WebSearchTool(BaseTool):
    """网络搜索工具（示例）"""
    name = "web_search"
    description = "在互联网上搜索信息。输入应该是搜索关键词。"
    
    def _run(self, query: str) -> str:
        """执行网络搜索"""
        try:
            # 这里是一个模拟的搜索结果
            # 在实际应用中，你需要接入真实的搜索API
            return f"搜索 '{query}' 的结果：找到相关信息，这是一个示例搜索结果。"
        except Exception as e:
            return f"搜索失败: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        """异步执行"""
        return self._run(query)

class ToolManager:
    """工具管理器"""
    
    def __init__(self):
        self.tools = {
            "calculator": CalculatorTool(),
            "current_time": CurrentTimeTool(),
            "weather": WeatherTool(),
            "web_search": WebSearchTool()
        }
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """获取指定名称的工具"""
        return self.tools.get(name)
    
    def get_all_tools(self) -> List[BaseTool]:
        """获取所有工具"""
        return list(self.tools.values())
    
    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """获取所有工具的schema定义"""
        schemas = []
        for tool in self.tools.values():
            schema = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "工具的输入参数"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
            schemas.append(schema)
        return schemas
    
    def execute_tool(self, tool_name: str, arguments: str) -> str:
        """执行指定的工具"""
        tool = self.get_tool(tool_name)
        if not tool:
            return f"工具 '{tool_name}' 不存在"
        
        try:
            # 解析参数
            if isinstance(arguments, str):
                try:
                    args = json.loads(arguments)
                    query = args.get('query', arguments)
                except json.JSONDecodeError:
                    query = arguments
            else:
                query = str(arguments)
            
            # 执行工具
            result = tool.run(query)
            return result
        except Exception as e:
            return f"工具执行错误: {str(e)}"
    
    async def aexecute_tool(self, tool_name: str, arguments: str) -> str:
        """异步执行指定的工具"""
        tool = self.get_tool(tool_name)
        if not tool:
            return f"工具 '{tool_name}' 不存在"
        
        try:
            # 解析参数
            if isinstance(arguments, str):
                try:
                    args = json.loads(arguments)
                    query = args.get('query', arguments)
                except json.JSONDecodeError:
                    query = arguments
            else:
                query = str(arguments)
            
            # 异步执行工具
            result = await tool.arun(query)
            return result
        except Exception as e:
            return f"工具执行错误: {str(e)}"

# 全局工具管理器实例
tool_manager = ToolManager()