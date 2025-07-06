#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
天气相关工具
"""

from langchain_core.tools import tool


@tool
def get_weather(city: str) -> str:
    """获取城市天气信息
    
    Args:
        city: 城市名称
    """
    # 模拟天气数据
    weather_data = {
        "北京": {"temperature": "15°C", "condition": "晴", "humidity": "45%"},
        "上海": {"temperature": "18°C", "condition": "多云", "humidity": "60%"},
        "广州": {"temperature": "25°C", "condition": "小雨", "humidity": "80%"},
        "深圳": {"temperature": "24°C", "condition": "晴", "humidity": "70%"},
        "杭州": {"temperature": "16°C", "condition": "阴", "humidity": "55%"},
    }
    
    if city in weather_data:
        weather = weather_data[city]
        return f"{city}的天气：温度{weather['temperature']}，{weather['condition']}，湿度{weather['humidity']}"
    else:
        return f"抱歉，暂时无法获取{city}的天气信息" 