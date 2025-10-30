# 📡 MCP Client 与 Server 完整实现

根据 [Issue #6](../issues/6) 的通信机制详解，实现完整的 MCP Client 和 Server。

## 🎯 项目概述

本项目提供了 **Model Context Protocol (MCP)** 的完整 Python 实现，包括：

- ✅ **MCP Server**: 支持 Tools、Resources、Prompts 三大核心功能
- ✅ **MCP Client**: 完整的客户端实现，支持所有 MCP 操作
- ✅ **JSON-RPC 2.0**: 标准协议实现
- ✅ **stdio 传输**: 本地进程间通信
- ✅ **示例代码**: 完整的使用示例和测试脚本

## 📦 文件结构

```
mcp-implementation/
├── mcp_server.py          # MCP Server 核心实现
├── mcp_client.py          # MCP Client 核心实现
├── example_usage.py       # 完整使用示例
├── test_communication.py  # 通信机制测试
├── config.json           # 配置文件示例
├── requirements.txt      # Python 依赖（无额外依赖）
└── README.md            # 本文档
```

## 🚀 快速开始

### 前置要求

- Python 3.8 或更高版本
- 无需额外依赖（仅使用标准库）

### 安装

```bash
# 克隆仓库
git clone https://github.com/chzhq0518/test-project.git
cd test-project/mcp-implementation

# 无需安装额外依赖
python --version  # 确保 Python 版本 >= 3.8
```

### 运行示例

#### 1️⃣ 运行 Server（单独测试）

```bash
python mcp_server.py
```

Server 将在 stdio 模式下运行，等待来自 stdin 的 JSON-RPC 请求。

#### 2️⃣ 运行 Client（连接到 Server）

```bash
python mcp_client.py
```

这将启动一个 Server 子进程，并演示所有功能。

#### 3️⃣ 运行完整示例

```bash
python example_usage.py
```

提供交互式菜单，可以选择运行不同的示例：
- 基本连接
- 工具调用
- 资源读取
- 提示词模板
- 错误处理
- 性能测试

#### 4️⃣ 运行测试套件

```bash
python test_communication.py
```

自动测试所有通信场景，验证实现的正确性。

## 📖 架构说明

### MCP 三层架构

```
┌─────────────────┐
│   MCP Host      │  应用程序（如 Cursor）
│  (应用层)       │
└────────┬────────┘
         │
┌────────▼────────┐
│   MCP Client    │  客户端 SDK
│  (客户端层)     │
└────────┬────────┘
         │ JSON-RPC 2.0
         │ (stdio)
┌────────▼────────┐
│   MCP Server    │  服务器实现
│  (服务器层)     │
└─────────────────┘
```

### 通信流程

1. **初始化阶段**
   ```
   Client → Server: initialize (协议版本、能力)
   Server → Client: initialize response (服务器信息)
   Client → Server: initialized notification
   ```

2. **功能发现阶段**
   ```
   Client → Server: tools/list
   Client → Server: resources/list
   Client → Server: prompts/list
   ```

3. **执行阶段**
   ```
   Client → Server: tools/call (工具调用)
   Client → Server: resources/read (资源读取)
   Client → Server: prompts/get (获取提示词)
   ```

## 🔧 使用指南

### 创建自定义 Server

```python
from mcp_server import MCPServer

# 创建 Server
server = MCPServer(name="my-server", version="1.0.0")

# 注册工具
def my_tool_handler(args):
    query = args.get("query")
    return f"处理查询: {query}"

server.register_tool(
    name="my_tool",
    description="我的自定义工具",
    input_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string"}
        },
        "required": ["query"]
    },
    handler=my_tool_handler
)

# 注册资源
def my_resource_handler():
    return "资源内容"

server.register_resource(
    uri="file:///my/resource",
    name="My Resource",
    description="我的资源",
    mime_type="text/plain",
    handler=my_resource_handler
)

# 注册提示词
def my_prompt_handler(args):
    return [{
        "role": "user",
        "content": {
            "type": "text",
            "text": "提示词内容"
        }
    }]

server.register_prompt(
    name="my_prompt",
    description="我的提示词",
    arguments=[],
    handler=my_prompt_handler
)

# 运行 Server
server.run()
```

### 使用 Client

```python
from mcp_client import MCPClient

# 使用上下文管理器
with MCPClient(["python", "mcp_server.py"]) as client:
    # 列出工具
    tools = client.list_tools()
    print(f"可用工具: {[t['name'] for t in tools]}")
    
    # 调用工具
    result = client.call_tool("search_code", {
        "query": "function",
        "path": "src/"
    })
    print(f"结果: {result}")
    
    # 列出资源
    resources = client.list_resources()
    
    # 读取资源
    content = client.read_resource(resources[0]['uri'])
    
    # 获取提示词
    prompt = client.get_prompt("code_review", {
        "language": "Python"
    })
```

## 📚 API 文档

### MCPServer

#### 方法

- `register_tool(name, description, input_schema, handler)` - 注册工具
- `register_resource(uri, name, description, mime_type, handler)` - 注册资源
- `register_prompt(name, description, arguments, handler)` - 注册提示词
- `run()` - 运行服务器主循环

### MCPClient

#### 方法

- `start()` - 启动连接
- `stop()` - 停止连接
- `list_tools()` - 获取工具列表
- `call_tool(name, arguments)` - 调用工具
- `list_resources()` - 获取资源列表
- `read_resource(uri)` - 读取资源
- `list_prompts()` - 获取提示词列表
- `get_prompt(name, arguments)` - 获取提示词

## 🧪 测试

运行测试套件验证所有功能：

```bash
python test_communication.py
```

测试覆盖：
- ✅ 初始化流程
- ✅ 工具发现和执行
- ✅ 资源发现和读取
- ✅ 提示词发现和获取
- ✅ JSON-RPC 格式验证
- ✅ 错误处理

## 📋 配置

### config.json 示例

```json
{
  "mcpServers": {
    "example": {
      "command": "python",
      "args": ["mcp_server.py"],
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  },
  "settings": {
    "timeout": 30,
    "protocolVersion": "2024-11-05"
  }
}
```

## 🔍 故障排查

### 问题：Server 无法启动

**解决方案：**
1. 检查 Python 版本：`python --version` (需要 >= 3.8)
2. 检查文件权限：`chmod +x mcp_server.py`
3. 查看错误日志（输出到 stderr）

### 问题：Client 连接超时

**解决方案：**
1. 确保 Server 脚本路径正确
2. 检查 Server 是否正常启动（查看 stderr 输出）
3. 增加超时时间：`client._send_request(method, params, timeout=60)`

### 问题：JSON 解析错误

**解决方案：**
1. 确保消息格式符合 JSON-RPC 2.0 规范
2. 检查编码格式（应为 UTF-8）
3. 查看详细日志（设置 `LOG_LEVEL=DEBUG`）

## 💡 最佳实践

### 1. 错误处理

```python
try:
    result = client.call_tool("my_tool", args)
except RuntimeError as e:
    print(f"工具执行失败: {e}")
except TimeoutError as e:
    print(f"请求超时: {e}")
```

### 2. 日志记录

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
```

### 3. 资源清理

```python
# 使用上下文管理器自动清理
with MCPClient(command) as client:
    # 使用 client
    pass
# 自动调用 stop()
```

### 4. 性能优化

- 批量操作时复用连接
- 缓存常用的工具/资源列表
- 使用合适的超时时间

## 🔗 相关资源

- [Issue #6: MCP Client 与 Server 通信机制详解](../issues/6)
- [MCP 官方文档](https://modelcontextprotocol.io/)
- [MCP 规范](https://spec.modelcontextprotocol.io/)
- [JSON-RPC 2.0 规范](https://www.jsonrpc.org/specification)

## 📝 协议规范

### JSON-RPC 2.0 消息格式

#### 请求
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "search_code",
    "arguments": {"query": "test"}
  }
}
```

#### 响应
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {"type": "text", "text": "结果"}
    ]
  }
}
```

#### 错误
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32601,
    "message": "Method not found"
  }
}
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

---

**注意：** 本实现仅用于学习和演示目的，生产环境使用请参考官方 SDK。
