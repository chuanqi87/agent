#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI Agent 工具模块
"""

from .datetime import get_current_time
from .calculator import calculate
from .weather import get_weather
from .random import generate_random

# 导出所有工具
__all__ = [
    "get_current_time",
    "calculate", 
    "get_weather",
    "generate_random",
]

# 工具列表
TOOLS = [
    get_current_time,
    calculate,
    get_weather, 
    generate_random,
] 