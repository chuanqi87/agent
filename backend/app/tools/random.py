#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
随机数相关工具
"""

import random
from langchain_core.tools import tool


@tool
def generate_random(count: int = 1, min_val: int = 1, max_val: int = 100) -> str:
    """生成随机数
    
    Args:
        count: 生成数量（默认1个）
        min_val: 最小值（默认1）
        max_val: 最大值（默认100）
    """
    try:
        if count > 10:
            return "生成数量不能超过10个"
        
        numbers = [random.randint(min_val, max_val) for _ in range(count)]
        
        if count == 1:
            return f"随机数：{numbers[0]}"
        else:
            return f"随机数列表：{', '.join(map(str, numbers))}"
    except Exception as e:
        return f"生成随机数失败：{str(e)}" 