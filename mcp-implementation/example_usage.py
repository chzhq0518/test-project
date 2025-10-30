#!/usr/bin/env python3
"""
完整的 MCP Client 和 Server 使用示例

演示如何:
1. 启动 MCP Server
2. 连接 Client 到 Server
3. 调用工具
4. 读取资源
5. 使用提示词模板
"""

import sys
import time
from mcp_client import MCPClient


def print_separator(title: str = "") -> None:
    """打印分隔线"""
    if title:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}\n")
    else:
        print(f"\n{'-'*60}\n")


def demo_basic_connection():
    """演示基本连接"""
    print_separator("1. 基本连接示例")
    
    with MCPClient(["python", "mcp_server.py"]) as client:
        print("✅ 成功连接到 MCP Server")
        print(f"服务器名称: {client.server_info.get('name')}")
        print(f"服务器版本: {client.server_info.get('version')}")
        print(f"协议版本: {client.server_capabilities}")


def demo_tools():
    """演示工具调用"""
    print_separator("2. 工具调用示例")
    
    with MCPClient(["python", "mcp_server.py"]) as client:
        # 列出所有工具
        print("📦 可用工具列表:")
        tools = client.list_tools()
        for i, tool in enumerate(tools, 1):
            print(f"\n  {i}. {tool['name']}")
            print(f"     描述: {tool['description']}")
            print(f"     参数: {tool['inputSchema']['properties'].keys()}")
        
        print_separator()
        
        # 调用搜索代码工具
        print("🔍 调用工具: search_code")
        print("参数: query='function login', path='src/'")
        result = client.call_tool("search_code", {
            "query": "function login",
            "path": "src/"
        })
        print(f"\n结果:\n{result}")
        
        print_separator()
        
        # 调用天气工具
        print("🌤️  调用工具: get_weather")
        for city in ["北京", "上海", "深圳"]:
            print(f"\n查询 {city} 的天气...")
            result = client.call_tool("get_weather", {"city": city})
            print(f"  {result}")


def demo_resources():
    """演示资源读取"""
    print_separator("3. 资源读取示例")
    
    with MCPClient(["python", "mcp_server.py"]) as client:
        # 列出所有资源
        print("📄 可用资源列表:")
        resources = client.list_resources()
        for i, resource in enumerate(resources, 1):
            print(f"\n  {i}. {resource['name']}")
            print(f"     URI: {resource['uri']}")
            print(f"     描述: {resource['description']}")
            print(f"     类型: {resource['mimeType']}")
        
        print_separator()
        
        # 读取资源
        if resources:
            resource = resources[0]
            print(f"📖 读取资源: {resource['name']}")
            print(f"URI: {resource['uri']}")
            content = client.read_resource(resource['uri'])
            print(f"\n内容:\n{content}")


def demo_prompts():
    """演示提示词模板"""
    print_separator("4. 提示词模板示例")
    
    with MCPClient(["python", "mcp_server.py"]) as client:
        # 列出所有提示词
        print("💬 可用提示词模板:")
        prompts = client.list_prompts()
        for i, prompt in enumerate(prompts, 1):
            print(f"\n  {i}. {prompt['name']}")
            print(f"     描述: {prompt['description']}")
            print(f"     参数: {[arg['name'] for arg in prompt['arguments']]}")
        
        print_separator()
        
        # 获取提示词
        if prompts:
            print("💬 获取提示词: code_review")
            for lang in ["Python", "JavaScript", "Java"]:
                print(f"\n语言: {lang}")
                prompt_result = client.get_prompt("code_review", {"language": lang})
                messages = prompt_result.get('messages', [])
                if messages:
                    print(f"提示词内容: {messages[0]['content']['text']}")


def demo_error_handling():
    """演示错误处理"""
    print_separator("5. 错误处理示例")
    
    with MCPClient(["python", "mcp_server.py"]) as client:
        # 调用不存在的工具
        print("❌ 测试调用不存在的工具...")
        try:
            client.call_tool("non_existent_tool", {})
        except RuntimeError as e:
            print(f"✅ 捕获到预期错误: {e}")
        
        print_separator()
        
        # 使用错误的参数
        print("❌ 测试缺少必需参数...")
        try:
            # search_code 需要 query 参数
            client.call_tool("search_code", {})
        except Exception as e:
            print(f"✅ 捕获到预期错误: {e}")
        
        print_separator()
        
        # 读取不存在的资源
        print("❌ 测试读取不存在的资源...")
        try:
            client.read_resource("file:///non/existent/file.txt")
        except RuntimeError as e:
            print(f"✅ 捕获到预期错误: {e}")


def demo_performance():
    """演示性能测试"""
    print_separator("6. 性能测试示例")
    
    with MCPClient(["python", "mcp_server.py"]) as client:
        # 批量调用工具
        print("⚡ 性能测试: 连续调用 10 次工具")
        
        cities = ["北京", "上海", "广州", "深圳", "杭州", 
                 "成都", "武汉", "西安", "南京", "重庆"]
        
        start_time = time.time()
        
        for i, city in enumerate(cities, 1):
            result = client.call_tool("get_weather", {"city": city})
            print(f"  {i}. {result}")
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n总耗时: {duration:.2f} 秒")
        print(f"平均每次: {duration/len(cities):.3f} 秒")
        print(f"QPS: {len(cities)/duration:.2f}")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("  MCP Client 和 Server 完整示例")
    print("  根据 issue #6 的通信机制实现")
    print("="*60)
    
    demos = [
        ("基本连接", demo_basic_connection),
        ("工具调用", demo_tools),
        ("资源读取", demo_resources),
        ("提示词模板", demo_prompts),
        ("错误处理", demo_error_handling),
        ("性能测试", demo_performance),
    ]
    
    print("\n请选择要运行的示例:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"  {i}. {name}")
    print(f"  0. 运行所有示例")
    
    try:
        choice = input("\n请输入选项 (0-6): ").strip()
        
        if choice == "0":
            for name, demo_func in demos:
                try:
                    demo_func()
                except Exception as e:
                    print(f"\n❌ 示例 '{name}' 执行出错: {e}")
                    import traceback
                    traceback.print_exc()
        elif choice.isdigit() and 1 <= int(choice) <= len(demos):
            name, demo_func = demos[int(choice) - 1]
            demo_func()
        else:
            print("\n❌ 无效的选项")
            return 1
        
        print("\n" + "="*60)
        print("  ✅ 示例执行完成")
        print("="*60 + "\n")
        return 0
    
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        return 130
    except Exception as e:
        print(f"\n❌ 执行出错: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
