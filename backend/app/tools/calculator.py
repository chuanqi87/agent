#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
计算相关工具
"""

import math
import re
from langchain_core.tools import tool


@tool
def calculate(expression: str) -> str:
    """计算数学表达式
    
    Args:
        expression: 要计算的数学表达式
    """
    try:
        # 安全的数学表达式计算
        
        # 清理表达式
        expr = expression.replace(" ", "")
        
        # 支持的数学函数
        safe_names = {
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "sqrt": math.sqrt,
            "abs": abs,
            "log": math.log,
            "exp": math.exp,
            "pi": math.pi,
            "e": math.e,
        }
        
        # 验证表达式安全性
        if not re.match(r'^[0-9+\-*/.()a-z ]+$', expr):
            return "表达式包含不安全字符"
        
        # 替换数学函数
        for name, func in safe_names.items():
            if isinstance(func, (int, float)):
                expr = expr.replace(name, str(func))
        
        # 使用eval计算（仅用于数学表达式）
        result = eval(expr, {"__builtins__": {}}, safe_names)
        
        return f"计算结果：{expression} = {result}"
        
    except Exception as e:
        return f"计算错误：{str(e)}" 