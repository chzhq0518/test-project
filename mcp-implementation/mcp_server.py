#!/usr/bin/env python3
"""
MCP Server 实现

根据 Model Context Protocol (MCP) 规范实现的服务器端
支持 JSON-RPC 2.0 协议和 stdio 传输
"""

import json
import sys
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum


# 配置日志（输出到 stderr 避免干扰 stdio 通信）
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)


class ErrorCode(Enum):
    """JSON-RPC 标准错误码"""
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603


@dataclass
class Tool:
    """工具定义"""
    name: str
    description: str
    inputSchema: Dict[str, Any]


@dataclass
class Resource:
    """资源定义"""
    uri: str
    name: str
    description: str
    mimeType: str


@dataclass
class Prompt:
    """提示词模板定义"""
    name: str
    description: str
    arguments: List[Dict[str, Any]]


class MCPServer:
    """MCP Server 核心实现"""
    
    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
        self.protocol_version = "2024-11-05"
        self.initialized = False
        
        # 注册的功能
        self.tools: Dict[str, Tool] = {}
        self.tool_handlers: Dict[str, Callable] = {}
        self.resources: Dict[str, Resource] = {}
        self.resource_handlers: Dict[str, Callable] = {}
        self.prompts: Dict[str, Prompt] = {}
        self.prompt_handlers: Dict[str, Callable] = {}
        
        # 注册内置方法
        self.methods = {
            "initialize": self._handle_initialize,
            "tools/list": self._handle_tools_list,
            "tools/call": self._handle_tools_call,
            "resources/list": self._handle_resources_list,
            "resources/read": self._handle_resources_read,
            "prompts/list": self._handle_prompts_list,
            "prompts/get": self._handle_prompts_get,
        }
    
    def register_tool(self, name: str, description: str, 
                     input_schema: Dict[str, Any], 
                     handler: Callable) -> None:
        """注册工具"""
        tool = Tool(name=name, description=description, inputSchema=input_schema)
        self.tools[name] = tool
        self.tool_handlers[name] = handler
        logger.info(f"Registered tool: {name}")
    
    def register_resource(self, uri: str, name: str, 
                         description: str, mime_type: str,
                         handler: Callable) -> None:
        """注册资源"""
        resource = Resource(uri=uri, name=name, 
                          description=description, mimeType=mime_type)
        self.resources[uri] = resource
        self.resource_handlers[uri] = handler
        logger.info(f"Registered resource: {uri}")
    
    def register_prompt(self, name: str, description: str,
                       arguments: List[Dict[str, Any]],
                       handler: Callable) -> None:
        """注册提示词模板"""
        prompt = Prompt(name=name, description=description, arguments=arguments)
        self.prompts[name] = prompt
        self.prompt_handlers[name] = handler
        logger.info(f"Registered prompt: {name}")
    
    def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理初始化请求"""
        client_protocol = params.get("protocolVersion")
        client_info = params.get("clientInfo", {})
        
        logger.info(f"Initialize from client: {client_info.get('name')} "
                   f"v{client_info.get('version')}")
        logger.info(f"Client protocol version: {client_protocol}")
        
        self.initialized = True
        
        return {
            "protocolVersion": self.protocol_version,
            "capabilities": {
                "resources": {},
                "tools": {},
                "prompts": {},
                "logging": {}
            },
            "serverInfo": {
                "name": self.name,
                "version": self.version
            }
        }
    
    def _handle_tools_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """列出所有可用工具"""
        tools_list = [asdict(tool) for tool in self.tools.values()]
        logger.debug(f"Listing {len(tools_list)} tools")
        return {"tools": tools_list}
    
    def _handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """调用工具"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name not in self.tool_handlers:
            raise ValueError(f"Tool not found: {tool_name}")
        
        logger.info(f"Calling tool: {tool_name} with args: {arguments}")
        
        try:
            handler = self.tool_handlers[tool_name]
            result = handler(arguments)
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": str(result)
                    }
                ],
                "isError": False
            }
        except Exception as e:
            logger.error(f"Tool execution error: {e}", exc_info=True)
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error: {str(e)}"
                    }
                ],
                "isError": True
            }
    
    def _handle_resources_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """列出所有可用资源"""
        resources_list = [asdict(res) for res in self.resources.values()]
        logger.debug(f"Listing {len(resources_list)} resources")
        return {"resources": resources_list}
    
    def _handle_resources_read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """读取资源"""
        uri = params.get("uri")
        
        if uri not in self.resource_handlers:
            raise ValueError(f"Resource not found: {uri}")
        
        logger.info(f"Reading resource: {uri}")
        
        handler = self.resource_handlers[uri]
        content = handler()
        
        return {
            "contents": [
                {
                    "uri": uri,
                    "mimeType": self.resources[uri].mimeType,
                    "text": content
                }
            ]
        }
    
    def _handle_prompts_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """列出所有可用提示词模板"""
        prompts_list = [asdict(prompt) for prompt in self.prompts.values()]
        logger.debug(f"Listing {len(prompts_list)} prompts")
        return {"prompts": prompts_list}
    
    def _handle_prompts_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取提示词模板"""
        prompt_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if prompt_name not in self.prompt_handlers:
            raise ValueError(f"Prompt not found: {prompt_name}")
        
        logger.info(f"Getting prompt: {prompt_name} with args: {arguments}")
        
        handler = self.prompt_handlers[prompt_name]
        messages = handler(arguments)
        
        return {
            "description": self.prompts[prompt_name].description,
            "messages": messages
        }
    
    def _create_error_response(self, request_id: Optional[Any], 
                              code: ErrorCode, 
                              message: str,
                              data: Optional[Dict] = None) -> Dict[str, Any]:
        """创建错误响应"""
        error = {
            "code": code.value,
            "message": message
        }
        if data:
            error["data"] = data
        
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": error
        }
        return response
    
    def _create_success_response(self, request_id: Any, 
                                result: Dict[str, Any]) -> Dict[str, Any]:
        """创建成功响应"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
    
    def _send_notification(self, method: str, params: Dict[str, Any]) -> None:
        """发送通知（无需响应的消息）"""
        notification = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }
        self._write_message(notification)
    
    def _write_message(self, message: Dict[str, Any]) -> None:
        """通过 stdout 发送消息"""
        output = json.dumps(message)
        sys.stdout.write(output + "\n")
        sys.stdout.flush()
        logger.debug(f"Sent: {output}")
    
    def handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """处理单个请求"""
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})
        
        # 检查是否是通知（没有 id）
        is_notification = request_id is None
        
        logger.debug(f"Handling {'notification' if is_notification else 'request'}: "
                    f"{method}")
        
        # 处理 initialized 通知
        if method == "notifications/initialized":
            logger.info("Client initialized notification received")
            return None
        
        # 查找处理方法
        if method not in self.methods:
            if is_notification:
                logger.warning(f"Unknown notification method: {method}")
                return None
            return self._create_error_response(
                request_id,
                ErrorCode.METHOD_NOT_FOUND,
                f"Method not found: {method}",
                {"method": method}
            )
        
        # 执行方法
        try:
            handler = self.methods[method]
            result = handler(params)
            
            if is_notification:
                return None
            
            return self._create_success_response(request_id, result)
        
        except ValueError as e:
            if is_notification:
                logger.error(f"Notification error: {e}")
                return None
            return self._create_error_response(
                request_id,
                ErrorCode.INVALID_PARAMS,
                str(e)
            )
        except Exception as e:
            logger.error(f"Internal error: {e}", exc_info=True)
            if is_notification:
                return None
            return self._create_error_response(
                request_id,
                ErrorCode.INTERNAL_ERROR,
                "Internal server error",
                {"details": str(e)}
            )
    
    def run(self) -> None:
        """运行服务器主循环（stdio 模式）"""
        logger.info(f"Starting MCP Server: {self.name} v{self.version}")
        logger.info("Listening on stdin...")
        
        try:
            for line in sys.stdin:
                line = line.strip()
                if not line:
                    continue
                
                logger.debug(f"Received: {line}")
                
                try:
                    request = json.loads(line)
                except json.JSONDecodeError as e:
                    logger.error(f"JSON parse error: {e}")
                    error_response = self._create_error_response(
                        None,
                        ErrorCode.PARSE_ERROR,
                        "Parse error"
                    )
                    self._write_message(error_response)
                    continue
                
                response = self.handle_request(request)
                
                if response:
                    self._write_message(response)
        
        except KeyboardInterrupt:
            logger.info("Server shutting down...")
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            sys.exit(1)


def create_example_server() -> MCPServer:
    """创建示例 MCP Server"""
    server = MCPServer(name="example-server", version="1.0.0")
    
    # 注册示例工具：搜索代码
    def search_code_handler(args: Dict[str, Any]) -> str:
        query = args.get("query")
        path = args.get("path", ".")
        return f"搜索结果：在 {path} 中找到 3 个匹配 '{query}' 的结果\n" \
               f"1. src/main.py:15\n" \
               f"2. src/utils.py:42\n" \
               f"3. src/api.py:8"
    
    server.register_tool(
        name="search_code",
        description="在代码库中搜索指定内容",
        input_schema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索关键词"
                },
                "path": {
                    "type": "string",
                    "description": "搜索路径（可选）"
                }
            },
            "required": ["query"]
        },
        handler=search_code_handler
    )
    
    # 注册示例工具：获取天气
    def get_weather_handler(args: Dict[str, Any]) -> str:
        city = args.get("city")
        return f"{city} 的天气：晴，温度 22°C，湿度 60%"
    
    server.register_tool(
        name="get_weather",
        description="获取指定城市的天气信息",
        input_schema={
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称"
                }
            },
            "required": ["city"]
        },
        handler=get_weather_handler
    )
    
    # 注册示例资源
    def readme_handler() -> str:
        return "# MCP Server Example\n\n这是一个示例 MCP Server 实现。"
    
    server.register_resource(
        uri="file:///project/README.md",
        name="README",
        description="项目说明文档",
        mime_type="text/markdown",
        handler=readme_handler
    )
    
    # 注册示例提示词
    def code_review_handler(args: Dict[str, Any]) -> List[Dict[str, Any]]:
        language = args.get("language", "Python")
        return [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": f"请审查以下 {language} 代码的质量、安全性和最佳实践。"
                }
            }
        ]
    
    server.register_prompt(
        name="code_review",
        description="代码审查提示词模板",
        arguments=[
            {
                "name": "language",
                "description": "编程语言",
                "required": True
            }
        ],
        handler=code_review_handler
    )
    
    return server


if __name__ == "__main__":
    server = create_example_server()
    server.run()
