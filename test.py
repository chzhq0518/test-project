#!/usr/bin/env python3
"""
测试脚本 - 用于测试GitHub MCP Server功能
"""

import json
import requests
from datetime import datetime

def test_function():
    """测试函数"""
    print("Hello from test-project!")
    print(f"当前时间: {datetime.now()}")
    return "测试成功"

def main():
    """主函数"""
    print("=== GitHub MCP Server 测试项目 ===")
    result = test_function()
    print(f"测试结果: {result}")

if __name__ == "__main__":
    main()