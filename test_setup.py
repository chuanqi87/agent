#!/usr/bin/env python3
"""
简单的设置测试脚本
验证依赖是否正确安装和基本功能是否正常
"""

import sys
import os
import importlib
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """测试关键模块导入"""
    print("正在测试依赖模块导入...")
    
    modules_to_test = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'langchain',
        'langserve',
        'httpx',
        'dotenv'
    ]
    
    failed_imports = []
    
    for module in modules_to_test:
        try:
            importlib.import_module(module)
            print(f"✓ {module} 导入成功")
        except ImportError as e:
            print(f"✗ {module} 导入失败: {str(e)}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n失败的模块: {', '.join(failed_imports)}")
        print("请运行 'pip install -r requirements.txt' 安装依赖")
        return False
    else:
        print("\n✓ 所有依赖模块导入成功")
        return True

def test_project_structure():
    """测试项目结构"""
    print("\n正在测试项目结构...")
    
    required_files = [
        'app/__init__.py',
        'app/config.py',
        'app/models.py',
        'app/tools.py',
        'app/chains.py',
        'app/server.py',
        'main.py',
        'requirements.txt',
        '.env.example'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path} 存在")
        else:
            print(f"✗ {file_path} 不存在")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n缺少的文件: {', '.join(missing_files)}")
        return False
    else:
        print("\n✓ 项目结构完整")
        return True

def test_environment_config():
    """测试环境配置"""
    print("\n正在测试环境配置...")
    
    # 测试是否存在环境变量文件
    if os.path.exists('.env'):
        print("✓ .env 文件存在")
        # 可以添加更多的环境变量验证
    else:
        print("! .env 文件不存在（正常，需要从 .env.example 复制）")
    
    if os.path.exists('.env.example'):
        print("✓ .env.example 文件存在")
    else:
        print("✗ .env.example 文件不存在")
        return False
    
    return True

def test_basic_functionality():
    """测试基本功能"""
    print("\n正在测试基本功能...")
    
    try:
        # 测试配置模块
        from app.config import config
        print("✓ 配置模块导入成功")
        
        # 测试模型模块
        from app.models import ChatCompletionRequest, Message, Role
        print("✓ 模型模块导入成功")
        
        # 测试工具模块
        from app.tools import tool_manager
        print("✓ 工具模块导入成功")
        
        # 测试工具数量
        tools = tool_manager.get_all_tools()
        print(f"✓ 加载了 {len(tools)} 个工具")
        
        # 测试FastAPI应用
        from app.server import app
        print("✓ FastAPI 应用创建成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 基本功能测试失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("=== LangServe Agent Backend 设置测试 ===\n")
    
    tests = [
        ("依赖模块导入", test_imports),
        ("项目结构", test_project_structure),
        ("环境配置", test_environment_config),
        ("基本功能", test_basic_functionality)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试出错: {str(e)}")
    
    print(f"\n=== 测试结果: {passed}/{total} 通过 ===")
    
    if passed == total:
        print("🎉 所有测试通过！项目设置正确。")
        print("\n下一步:")
        print("1. 复制 .env.example 到 .env")
        print("2. 编辑 .env 文件，设置您的 OPENAI_API_KEY")
        print("3. 运行 './run.sh' 或 'python main.py' 启动服务器")
    else:
        print("❌ 部分测试失败，请检查上述错误信息。")
        sys.exit(1)

if __name__ == "__main__":
    main()