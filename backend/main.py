#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from app.server import create_app
from app.config import get_settings

def main():
    """应用入口"""
    app = create_app()
    
    # 使用配置类获取设置
    settings = get_settings()
    
    print(f"🚀 启动AI Agent后端服务...")
    print(f"📡 服务地址: http://{settings.APP_HOST}:{settings.APP_PORT}")
    print(f"🔧 调试模式: {settings.DEBUG}")
    print(f"🤖 当前模型提供商: {settings.MODEL_PROVIDER}")
    
    # 显示当前模型配置
    model_config = settings.get_active_model_config()
    print(f"🎯 使用模型: {model_config['model']} ({model_config['provider']})")
    
    import uvicorn
    uvicorn.run(
        "app.server:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
        log_level="info"
    )

if __name__ == "__main__":
    main() 