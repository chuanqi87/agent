#!/bin/bash
# LangServe Agent Backend 启动脚本

echo "正在启动 LangServe Agent Backend..."

# 检查Python版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python版本: $python_version"

# 检查是否存在虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo "警告: .env文件不存在，请复制.env.example并配置您的API密钥"
    echo "cp .env.example .env"
    echo "然后编辑.env文件，设置您的OPENAI_API_KEY"
    exit 1
fi

# 启动服务器
echo "启动服务器..."
python main.py