from dataclasses import dataclass
from typing import List, Optional, Any, Dict, List
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@dataclass
class MCPServer:
    id: str
    name: str
    command: str
    args: List[str]


@dataclass
class MCPTool:
    name: str
    description: str
    input_schema: Dict[str, Any]


class MCPClient:
    def __init__(self):
        self.write = None
        self.stdio = None
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

    async def connet_to_server(self, mcp_servers: List[MCPServer]) -> List[MCPTool]:
        """
        连接mcp server
        """

        available_tools = []
        for server in mcp_servers:
            server_params = StdioServerParameters(
                command=server.command,
                args=server.args,
                env=None
            )

            stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
            self.stdio, self.write = stdio_transport
            self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

            await self.session.initialize()

            # List available tools
            response = await self.session.list_tools()
            for tool in response.tools:
                available_tools.append(MCPTool(
                    name=tool.name,
                    description=tool.description,
                    input_schema=tool.inputSchema,
                ))

        return available_tools

    async def tools_call(self, tools: List) -> List:
        results = []
        for tool in tools:
            tool_name = tool["tool_name"]
            tool_args = tool["tool_args"]
            print(f"\n\n开始调用工具{tool_name}, 调用参数: {tool_args}")
            result = await self.session.call_tool(tool_name, tool_args)
            print(f"调用结果: {result}")
            results.append(result.content)
        return results
