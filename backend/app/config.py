#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """应用配置"""
    
    # 模型配置
    MODEL_PROVIDER: str = "deepseek"  # 支持: "deepseek", "gemini", "openai" 
    
    # DeepSeek配置
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    
    # Gemini配置
    GEMINI_API_KEY: str = ""
    GEMINI_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta"
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"
    
    # OpenAI配置
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4"
    
    # 应用配置
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = True
    
    # CORS配置
    FRONTEND_URL: str = "http://localhost:5173"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def get_active_model_config(self) -> dict:
        """根据MODEL_PROVIDER返回当前激活的模型配置"""
        if self.MODEL_PROVIDER.lower() == "deepseek":
            return {
                "api_key": self.DEEPSEEK_API_KEY,
                "base_url": self.DEEPSEEK_BASE_URL,
                "model": self.DEEPSEEK_MODEL,
                "provider": "deepseek"
            }
        elif self.MODEL_PROVIDER.lower() == "gemini":
            return {
                "api_key": self.GEMINI_API_KEY,
                "base_url": self.GEMINI_BASE_URL,
                "model": self.GEMINI_MODEL,
                "provider": "gemini"
            }
        elif self.MODEL_PROVIDER.lower() == "openai":
            return {
                "api_key": self.OPENAI_API_KEY,
                "base_url": self.OPENAI_BASE_URL,
                "model": self.OPENAI_MODEL,
                "provider": "openai"
            }
        else:
            # 默认使用deepseek
            return {
                "api_key": self.DEEPSEEK_API_KEY,
                "base_url": self.DEEPSEEK_BASE_URL,
                "model": self.DEEPSEEK_MODEL,
                "provider": "deepseek"
            }

def get_settings() -> Settings:
    """获取应用配置"""
    return Settings() 