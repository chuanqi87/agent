#!/usr/bin/env python3
"""
LangServe Agent Backend - 主程序入口
基于LangChain和LangServe构建的AI Agent后端，提供OpenAI兼容的API接口
"""

import uvicorn
import logging
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.config import config
from app.server import app

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """主函数"""
    try:
        # 验证配置
        config.validate()
        
        # 启动服务器
        logger.info(f"启动 LangServe Agent API 服务器...")
        logger.info(f"地址: http://{config.HOST}:{config.PORT}")
        logger.info(f"API文档: http://{config.HOST}:{config.PORT}/docs")
        logger.info(f"模型: {config.DEFAULT_MODEL}")
        logger.info(f"工具功能: {'启用' if config.ENABLE_TOOLS else '禁用'}")
        
        # 运行服务器
        uvicorn.run(
            app,
            host=config.HOST,
            port=config.PORT,
            log_level="info",
            access_log=True
        )
        
    except Exception as e:
        logger.error(f"启动服务器时发生错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()