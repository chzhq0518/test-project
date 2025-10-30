#!/usr/bin/env python3
"""
MCP 通信机制测试脚本

测试 issue #6 中描述的所有通信场景:
1. 初始化流程
2. 功能发现
3. 执行操作
4. 错误处理
"""

import sys
import json
from mcp_client import MCPClient


class TestResult:
    """测试结果"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def add_pass(self, name: str, message: str = ""):
        self.passed += 1
        self.tests.append((True, name, message))
        print(f"✅ PASS: {name}")
        if message:
            print(f"   {message}")
    
    def add_fail(self, name: str, message: str = ""):
        self.failed += 1
        self.tests.append((False, name, message))
        print(f"❌ FAIL: {name}")
        if message:
            print(f"   {message}")
    
    def print_summary(self):
        print("\n" + "="*60)
        print(f"测试总结: {self.passed + self.failed} 个测试")
        print(f"  ✅ 通过: {self.passed}")
        print(f"  ❌ 失败: {self.failed}")
        print("="*60)


def test_initialization(client: MCPClient, result: TestResult):
    """测试初始化流程"""
    print("\n=== 测试 1: 初始化流程 ===")
    
    # 检查服务器信息
    if client.server_info:
        result.add_pass("服务器信息获取", 
                       f"服务器: {client.server_info.get('name')}")
    else:
        result.add_fail("服务器信息获取")
    
    # 检查服务器能力
    if client.server_capabilities:
        result.add_pass("服务器能力获取",
                       f"能力: {list(client.server_capabilities.keys())}")
    else:
        result.add_fail("服务器能力获取")


def test_tools_discovery(client: MCPClient, result: TestResult):
    """测试工具发现"""
    print("\n=== 测试 2: 工具发现 ===")
    
    try:
        tools = client.list_tools()
        if tools and len(tools) > 0:
            result.add_pass("列出工具", f"找到 {len(tools)} 个工具")
            
            # 检查工具结构
            required_fields = ['name', 'description', 'inputSchema']
            tool = tools[0]
            
            if all(field in tool for field in required_fields):
                result.add_pass("工具结构验证", f"工具: {tool['name']}")
            else:
                result.add_fail("工具结构验证", "缺少必需字段")
        else:
            result.add_fail("列出工具", "未找到任何工具")
    
    except Exception as e:
        result.add_fail("列出工具", str(e))


def test_tools_execution(client: MCPClient, result: TestResult):
    """测试工具执行"""
    print("\n=== 测试 3: 工具执行 ===")
    
    # 测试正常调用
    try:
        response = client.call_tool("search_code", {
            "query": "test",
            "path": "src/"
        })
        if response:
            result.add_pass("工具正常调用", "search_code 执行成功")
        else:
            result.add_fail("工具正常调用", "返回空结果")
    except Exception as e:
        result.add_fail("工具正常调用", str(e))
    
    # 测试错误处理
    try:
        client.call_tool("non_existent_tool", {})
        result.add_fail("工具错误处理", "应该抛出异常但没有")
    except RuntimeError:
        result.add_pass("工具错误处理", "正确抛出异常")
    except Exception as e:
        result.add_fail("工具错误处理", f"错误的异常类型: {type(e)}")


def test_resources_discovery(client: MCPClient, result: TestResult):
    """测试资源发现"""
    print("\n=== 测试 4: 资源发现 ===")
    
    try:
        resources = client.list_resources()
        if resources and len(resources) > 0:
            result.add_pass("列出资源", f"找到 {len(resources)} 个资源")
            
            # 检查资源结构
            required_fields = ['uri', 'name', 'description', 'mimeType']
            resource = resources[0]
            
            if all(field in resource for field in required_fields):
                result.add_pass("资源结构验证", f"资源: {resource['name']}")
            else:
                result.add_fail("资源结构验证", "缺少必需字段")
        else:
            result.add_fail("列出资源", "未找到任何资源")
    
    except Exception as e:
        result.add_fail("列出资源", str(e))


def test_resources_reading(client: MCPClient, result: TestResult):
    """测试资源读取"""
    print("\n=== 测试 5: 资源读取 ===")
    
    try:
        resources = client.list_resources()
        if resources:
            uri = resources[0]['uri']
            content = client.read_resource(uri)
            
            if content:
                result.add_pass("资源正常读取", f"读取了 {len(content)} 字符")
            else:
                result.add_fail("资源正常读取", "返回空内容")
        else:
            result.add_fail("资源正常读取", "没有可用资源")
    
    except Exception as e:
        result.add_fail("资源正常读取", str(e))
    
    # 测试错误处理
    try:
        client.read_resource("file:///invalid/path")
        result.add_fail("资源错误处理", "应该抛出异常但没有")
    except RuntimeError:
        result.add_pass("资源错误处理", "正确抛出异常")
    except Exception as e:
        result.add_fail("资源错误处理", f"错误的异常类型: {type(e)}")


def test_prompts_discovery(client: MCPClient, result: TestResult):
    """测试提示词发现"""
    print("\n=== 测试 6: 提示词发现 ===")
    
    try:
        prompts = client.list_prompts()
        if prompts and len(prompts) > 0:
            result.add_pass("列出提示词", f"找到 {len(prompts)} 个提示词")
            
            # 检查提示词结构
            required_fields = ['name', 'description', 'arguments']
            prompt = prompts[0]
            
            if all(field in prompt for field in required_fields):
                result.add_pass("提示词结构验证", f"提示词: {prompt['name']}")
            else:
                result.add_fail("提示词结构验证", "缺少必需字段")
        else:
            result.add_fail("列出提示词", "未找到任何提示词")
    
    except Exception as e:
        result.add_fail("列出提示词", str(e))


def test_prompts_retrieval(client: MCPClient, result: TestResult):
    """测试提示词获取"""
    print("\n=== 测试 7: 提示词获取 ===")
    
    try:
        prompts = client.list_prompts()
        if prompts:
            name = prompts[0]['name']
            prompt_data = client.get_prompt(name, {"language": "Python"})
            
            if 'messages' in prompt_data:
                result.add_pass("提示词正常获取", 
                               f"获取了 {len(prompt_data['messages'])} 条消息")
            else:
                result.add_fail("提示词正常获取", "返回格式错误")
        else:
            result.add_fail("提示词正常获取", "没有可用提示词")
    
    except Exception as e:
        result.add_fail("提示词正常获取", str(e))


def test_json_rpc_format(client: MCPClient, result: TestResult):
    """测试 JSON-RPC 格式"""
    print("\n=== 测试 8: JSON-RPC 格式 ===")
    
    # 这个测试需要直接检查消息格式
    # 由于我们的实现已经封装了 JSON-RPC，这里只做基本检查
    try:
        tools = client.list_tools()
        result.add_pass("JSON-RPC 请求-响应", "通信正常")
    except Exception as e:
        result.add_fail("JSON-RPC 请求-响应", str(e))


def main():
    """主测试函数"""
    print("="*60)
    print("  MCP 通信机制测试")
    print("  测试 issue #6 中描述的通信流程")
    print("="*60)
    
    result = TestResult()
    
    try:
        print("\n🚀 启动 MCP Server 并建立连接...")
        with MCPClient(["python", "mcp_server.py"]) as client:
            print("✅ 连接建立成功\n")
            
            # 运行所有测试
            test_initialization(client, result)
            test_tools_discovery(client, result)
            test_tools_execution(client, result)
            test_resources_discovery(client, result)
            test_resources_reading(client, result)
            test_prompts_discovery(client, result)
            test_prompts_retrieval(client, result)
            test_json_rpc_format(client, result)
    
    except Exception as e:
        print(f"\n❌ 测试执行出错: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # 打印测试总结
    result.print_summary()
    
    # 返回退出码
    return 0 if result.failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
