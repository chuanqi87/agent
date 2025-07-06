#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
时间相关工具
"""

import datetime
import pytz
from langchain_core.tools import tool


@tool
def get_current_time(format: str = "datetime", timezone: str = "Asia/Shanghai") -> str:
    """获取当前时间
    
    Args:
        format: 时间格式 (datetime, date, time, timestamp)
        timezone: 时区
    """
    try:
        if timezone == "UTC":
            tz = pytz.UTC
        else:
            tz = pytz.timezone(timezone)
        
        now = datetime.datetime.now(tz)
        
        if format == "date":
            return f"当前日期：{now.strftime('%Y-%m-%d')}"
        elif format == "time":
            return f"当前时间：{now.strftime('%H:%M:%S')}"
        elif format == "timestamp":
            return f"当前时间戳：{int(now.timestamp())}"
        else:
            return f"当前时间：{now.strftime('%Y-%m-%d %H:%M:%S %Z')}"
    except Exception as e:
        return f"获取时间失败：{str(e)}" 