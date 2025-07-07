import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # OpenAI API配置
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    # 服务器配置
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    
    # 模型配置
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", 4096))
    TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))
    
    # Agent配置
    AGENT_NAME = os.getenv("AGENT_NAME", "LangServe Agent")
    AGENT_DESCRIPTION = os.getenv("AGENT_DESCRIPTION", "A powerful AI agent with tool calling capabilities")
    
    # 工具配置
    ENABLE_TOOLS = os.getenv("ENABLE_TOOLS", "true").lower() == "true"
    
    @classmethod
    def validate(cls):
        """验证必需的配置项"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        return True

config = Config()