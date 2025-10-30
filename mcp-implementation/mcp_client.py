#!/usr/bin/env python3
"""
MCP Client 实现

根据 Model Context Protocol (MCP) 规范实现的客户端
支持 JSON-RPC 2.0 协议和 stdio 传输
"""

import json
import subprocess
import logging
import threading
from typing import Dict, List, Any, Optional, Callable
from queue import Queue, Empty
import time


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MCPClient:
    """MCP Client 核心实现"""
    
    def __init__(self, command: List[str], env: Optional[Dict[str, str]] = None):
        """
        初始化 MCP Client
        
        Args:
            command: 启动 MCP Server 的命令（如 ["python", "mcp_server.py"]）
            env: 环境变量
        """
        self.command = command
        self.env = env
        self.process: Optional[subprocess.Popen] = None
        self.next_id = 1
        self.pending_requests: Dict[int, Queue] = {}
        self.reader_thread: Optional[threading.Thread] = None
        self.running = False
        
        # 服务器信息
        self.server_info: Optional[Dict[str, Any]] = None
        self.server_capabilities: Optional[Dict[str, Any]] = None
        
    def start(self) -> None:
        """启动 MCP Server 进程并建立连接"""
        logger.info(f"Starting MCP Server: {' '.join(self.command)}")
        
        # 启动子进程
        self.process = subprocess.Popen(
            self.command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self.env,
            text=True,
            bufsize=1
        )
        
        # 启动读取线程
        self.running = True
        self.reader_thread = threading.Thread(target=self._read_loop, daemon=True)
        self.reader_thread.start()
        
        # 启动错误日志线程
        stderr_thread = threading.Thread(target=self._stderr_loop, daemon=True)
        stderr_thread.start()
        
        # 等待一下确保进程启动
        time.sleep(0.5)
        
        # 发送初始化请求
        self._initialize()
        
        logger.info("MCP Client connected successfully")
    
    def stop(self) -> None:
        """停止 MCP Client 并关闭连接"""
        logger.info("Stopping MCP Client...")
        
        self.running = False
        
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("Process didn't terminate, killing...")
                self.process.kill()
                self.process.wait()
        
        if self.reader_thread:
            self.reader_thread.join(timeout=2)
        
        logger.info("MCP Client stopped")
    
    def _read_loop(self) -> None:
        """读取服务器响应的循环"""
        if not self.process or not self.process.stdout:
            return
        
        logger.debug("Reader thread started")
        
        try:
            for line in self.process.stdout:
                if not self.running:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                logger.debug(f"Received: {line}")
                
                try:
                    message = json.loads(line)
                    self._handle_message(message)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON: {e}")
                except Exception as e:
                    logger.error(f"Error handling message: {e}", exc_info=True)
        
        except Exception as e:
            logger.error(f"Reader thread error: {e}", exc_info=True)
        
        logger.debug("Reader thread stopped")
    
    def _stderr_loop(self) -> None:
        """读取服务器 stderr 的循环"""
        if not self.process or not self.process.stderr:
            return
        
        try:
            for line in self.process.stderr:
                if not self.running:
                    break
                line = line.strip()
                if line:
                    logger.debug(f"[Server] {line}")
        except Exception as e:
            logger.error(f"Stderr thread error: {e}")
    
    def _handle_message(self, message: Dict[str, Any]) -> None:
        """处理收到的消息"""
        # 检查是否是响应
        if "id" in message and message["id"] in self.pending_requests:
            request_id = message["id"]
            queue = self.pending_requests[request_id]
            queue.put(message)
        
        # 检查是否是通知
        elif "method" in message and "id" not in message:
            method = message.get("method")
            params = message.get("params", {})
            logger.info(f"Received notification: {method} with params: {params}")
        
        else:
            logger.warning(f"Received unexpected message: {message}")
    
    def _send_request(self, method: str, params: Optional[Dict[str, Any]] = None,
                     timeout: float = 30.0) -> Dict[str, Any]:
        """
        发送请求并等待响应
        
        Args:
            method: 方法名
            params: 参数
            timeout: 超时时间（秒）
        
        Returns:
            响应结果
        
        Raises:
            TimeoutError: 请求超时
            RuntimeError: 服务器返回错误
        """
        if not self.process or not self.process.stdin:
            raise RuntimeError("Client not connected")
        
        request_id = self.next_id
        self.next_id += 1
        
        request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method
        }
        
        if params is not None:
            request["params"] = params
        
        # 创建响应队列
        response_queue: Queue = Queue()
        self.pending_requests[request_id] = response_queue
        
        # 发送请求
        try:
            request_json = json.dumps(request)
            logger.debug(f"Sending: {request_json}")
            self.process.stdin.write(request_json + "\n")
            self.process.stdin.flush()
        except Exception as e:
            del self.pending_requests[request_id]
            raise RuntimeError(f"Failed to send request: {e}")
        
        # 等待响应
        try:
            response = response_queue.get(timeout=timeout)
        except Empty:
            del self.pending_requests[request_id]
            raise TimeoutError(f"Request timeout after {timeout}s")
        finally:
            if request_id in self.pending_requests:
                del self.pending_requests[request_id]
        
        # 检查错误
        if "error" in response:
            error = response["error"]
            raise RuntimeError(
                f"Server error: {error.get('message')} "
                f"(code: {error.get('code')})"
            )
        
        return response.get("result", {})
    
    def _send_notification(self, method: str, 
                          params: Optional[Dict[str, Any]] = None) -> None:
        """发送通知（无需响应）"""
        if not self.process or not self.process.stdin:
            raise RuntimeError("Client not connected")
        
        notification = {
            "jsonrpc": "2.0",
            "method": method
        }
        
        if params is not None:
            notification["params"] = params
        
        notification_json = json.dumps(notification)
        logger.debug(f"Sending notification: {notification_json}")
        self.process.stdin.write(notification_json + "\n")
        self.process.stdin.flush()
    
    def _initialize(self) -> None:
        """初始化连接"""
        logger.info("Initializing connection...")
        
        result = self._send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "roots": {
                    "listChanged": True
                },
                "sampling": {}
            },
            "clientInfo": {
                "name": "mcp-python-client",
                "version": "1.0.0"
            }
        })
        
        self.server_info = result.get("serverInfo", {})
        self.server_capabilities = result.get("capabilities", {})
        
        logger.info(f"Connected to server: {self.server_info.get('name')} "
                   f"v{self.server_info.get('version')}")
        logger.debug(f"Server capabilities: {self.server_capabilities}")
        
        # 发送初始化完成通知
        self._send_notification("notifications/initialized")
    
    # === 高级 API ===
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """获取可用工具列表"""
        result = self._send_request("tools/list")
        return result.get("tools", [])
    
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """
        调用工具
        
        Args:
            name: 工具名称
            arguments: 工具参数
        
        Returns:
            工具执行结果
        """
        result = self._send_request("tools/call", {
            "name": name,
            "arguments": arguments
        })
        
        content = result.get("content", [])
        if content and len(content) > 0:
            return content[0].get("text", "")
        
        return ""
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """获取可用资源列表"""
        result = self._send_request("resources/list")
        return result.get("resources", [])
    
    def read_resource(self, uri: str) -> str:
        """
        读取资源
        
        Args:
            uri: 资源 URI
        
        Returns:
            资源内容
        """
        result = self._send_request("resources/read", {"uri": uri})
        
        contents = result.get("contents", [])
        if contents and len(contents) > 0:
            return contents[0].get("text", "")
        
        return ""
    
    def list_prompts(self) -> List[Dict[str, Any]]:
        """获取可用提示词模板列表"""
        result = self._send_request("prompts/list")
        return result.get("prompts", [])
    
    def get_prompt(self, name: str, 
                   arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        获取提示词模板
        
        Args:
            name: 模板名称
            arguments: 模板参数
        
        Returns:
            提示词模板内容
        """
        params = {"name": name}
        if arguments:
            params["arguments"] = arguments
        
        return self._send_request("prompts/get", params)
    
    def __enter__(self):
        """上下文管理器入口"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.stop()


def main():
    """示例：使用 MCP Client 连接到服务器"""
    print("=== MCP Client 示例 ===\n")
    
    # 使用上下文管理器自动管理连接
    with MCPClient(["python", "mcp_server.py"]) as client:
        print(f"✅ 已连接到服务器: {client.server_info}\n")
        
        # 列出所有工具
        print("📦 可用工具:")
        tools = client.list_tools()
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description']}")
        print()
        
        # 调用工具
        print("🔧 调用工具: search_code")
        result = client.call_tool("search_code", {
            "query": "function login",
            "path": "src/"
        })
        print(f"结果:\n{result}\n")
        
        # 调用天气工具
        print("🔧 调用工具: get_weather")
        result = client.call_tool("get_weather", {"city": "北京"})
        print(f"结果: {result}\n")
        
        # 列出资源
        print("📄 可用资源:")
        resources = client.list_resources()
        for resource in resources:
            print(f"  - {resource['name']} ({resource['uri']})")
        print()
        
        # 读取资源
        if resources:
            uri = resources[0]['uri']
            print(f"📖 读取资源: {uri}")
            content = client.read_resource(uri)
            print(f"内容:\n{content}\n")
        
        # 列出提示词
        print("💬 可用提示词:")
        prompts = client.list_prompts()
        for prompt in prompts:
            print(f"  - {prompt['name']}: {prompt['description']}")
        print()
        
        # 获取提示词
        if prompts:
            print("💬 获取提示词: code_review")
            prompt_result = client.get_prompt("code_review", {"language": "Python"})
            print(f"提示词: {prompt_result}\n")
    
    print("✅ 示例完成")


if __name__ == "__main__":
    main()
