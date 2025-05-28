import json
import re

from mcp_client import MCPClient, MCPServer, MCPTool
from langchain_openai import ChatOpenAI
from typing import List, Dict, Any

mcp_prompt = """
In this environment you have access to a set of tools you can use to answer the user's question. \
You can use one tool per message, and will receive the result of that tool use in the user's response. You use tools step-by-step to accomplish a given task, with each tool use informed by the result of the previous tool use.

## Tool Use Formatting

Tool use is formatted using XML-style tags. The tool name is enclosed in opening and closing tags, and each parameter is similarly enclosed within its own set of tags. Here's the structure:

<tool_use>
  <name>{{tool_name}}</name>
  <arguments>{{json_arguments}}</arguments>
</tool_use>

The tool name should be the exact name of the tool you are using, and the arguments should be a JSON object containing the parameters required by that tool. For example:
<tool_use>
  <name>python_interpreter</name>
  <arguments>{{"code": "5 + 3 + 1294.678"}}</arguments>
</tool_use>

The user will respond with the result of the tool use, which should be formatted as follows:

<tool_use_result>
  <name>{{tool_name}}</name>
  <result>{{result}}</result>
</tool_use_result>

The result should be a string, which can represent a file or any other output type. You can use this result as input for the next action.
For example, if the result of the tool use is an image file, you can use it in the next action like this:

<tool_use>
  <name>image_transformer</name>
  <arguments>{{"image": "image_1.jpg"}}</arguments>
</tool_use>

Always adhere to this format for the tool use to ensure proper parsing and execution.

## Tool Use Examples
Here are a few examples using notional tools:
---
User: Generate an image of the oldest person in this document.

Assistant: I can use the document_qa tool to find out who the oldest person is in the document.
<tool_use>
  <name>document_qa</name>
  <arguments>{{"document": "document.pdf", "question": "Who is the oldest person mentioned?"}}</arguments>
</tool_use>

User: <tool_use_result>
  <name>document_qa</name>
  <result>John Doe, a 55 year old lumberjack living in Newfoundland.</result>
</tool_use_result>

Assistant: I can use the image_generator tool to create a portrait of John Doe.
<tool_use>
  <name>image_generator</name>
  <arguments>{{"prompt": "A portrait of John Doe, a 55-year-old man living in Canada."}}</arguments>
</tool_use>

User: <tool_use_result>
  <name>image_generator</name>
  <result>image.png</result>
</tool_use_result>

Assistant: the image is generated as image.png

---
User: "What is the result of the following operation: 5 + 3 + 1294.678?"

Assistant: I can use the python_interpreter tool to calculate the result of the operation.
<tool_use>
  <name>python_interpreter</name>
  <arguments>{{"code": "5 + 3 + 1294.678"}}</arguments>
</tool_use>

User: <tool_use_result>
  <name>python_interpreter</name>
  <result>1302.678</result>
</tool_use_result>

Assistant: The result of the operation is 1302.678.

---
User: "Which city has the highest population , Guangzhou or Shanghai?"

Assistant: I can use the search tool to find the population of Guangzhou.
<tool_use>
  <name>search</name>
  <arguments>{{"query": "Population Guangzhou"}}</arguments>
</tool_use>

User: <tool_use_result>
  <name>search</name>
  <result>Guangzhou has a population of 15 million inhabitants as of 2021.</result>
</tool_use_result>

Assistant: I can use the search tool to find the population of Shanghai.
<tool_use>
  <name>search</name>
  <arguments>{{"query": "Population Shanghai"}}</arguments>
</tool_use>

User: <tool_use_result>
  <name>search</name>
  <result>26 million (2019)</result>
</tool_use_result>
Assistant: The population of Shanghai is 26 million, while Guangzhou has a population of 15 million. Therefore, Shanghai has the highest population.

## Tool Use Available Tools
Above example were using notional tools that might not exist for you. You only have access to these tools:
{available_tools}

## Tool Use Rules
Here are the rules you should always follow to solve your task:
1. Always use the right arguments for the tools. Never use variable names as the action arguments, use the value instead.
2. Call a tool only when needed: do not call the search agent if you do not need information, try to solve the task yourself.
3. If no tool call is needed, just answer the question directly.
4. Never re-do a tool call that you previously did with the exact same parameters.
5. For tool use, MARK SURE use XML tag format as shown in the examples above. Do not use any other format.

# User Instructions
{user_system_prompt}

Now Begin! If you solve the task correctly, you will receive a reward of $1,000,000.
"""


class LLMClient:
    def __init__(self, model: str, base_url: str, api_key: str):
        self.model_client = ChatOpenAI(model=model, base_url=base_url, api_key=api_key)
        self.mcp_client: MCPClient = MCPClient()
        self.available_tools: List[MCPTool] = []
        self.mcp_servers: List[MCPServer] = []
        self.system_prompt: str = ""

    def add_mcp_server(self, mcp_server: MCPServer):
        """
        添加mcp server
        """

        self.mcp_servers.append(mcp_server)

    async def get_mcp_tools(self):
        """
        获取mcp工具
        """

        self.available_tools = await self.mcp_client.connet_to_server(self.mcp_servers)

    async def generate_mcp_prompt(self) -> str:
        """
        生成mcp提示词
        """

        tool_prompt = ""
        for tool in self.available_tools:
            tool_prompt += (f"\n<tool_use>\n<name>{tool.name}</name>\n<description>{tool.description}</description>\n"
                           f"<arguments>{tool.input_schema}</arguments>\n</tool_use>\n")
        return mcp_prompt.format(available_tools=tool_prompt, user_system_prompt=self.system_prompt)

    async def parse_tool_use(self, resp_content: str) -> List[Dict[str, Any]]:
        """
        解析大模型工具调用
        """

        tool_use_pattern = r'<tool_use>([\s\S]*?)<name>([\s\S]*?)<\/name>([\s\S]*?)<arguments>([\s\S]*?)<\/arguments>([\s\S]*?)<\/tool_use>'
        tools = []

        for match in re.finditer(tool_use_pattern, resp_content):
            tool_name = match.group(2).strip()
            tool_args = match.group(4).strip()

            try:
                parsed_args = json.loads(tool_args)
            except json.JSONDecodeError:
                parsed_args = {}

            mcp_tool = next((tool for tool in self.available_tools if tool.name == tool_name), None)
            if mcp_tool:
                tools.append({
                    "tool_name": tool_name,
                    "tool_args": parsed_args
                })
        return tools

    async def chat(self, user_message: str):
        # 添加系统提示词
        system_prompt = self.system_prompt
        # 如果有mcp工具,附加mcp工具调用系统提示
        if self.available_tools:
            system_prompt = await self.generate_mcp_prompt()

        message = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        assistant_content = ""
        # 第一次请求大模型
        async for chunk in self.model_client.astream(message):
            if hasattr(chunk, "content") and chunk.content:
                print(chunk.content, end="", flush=True)
                assistant_content += chunk.content

        tools_call = await self.parse_tool_use(assistant_content)

        while tools_call:
            print("tool use")
            results = await self.mcp_client.tools_call(tools_call)
            message.append({"role": "assistant", "content": assistant_content})
            message.append({"role": "user", "content": results})

            assistant_content = ""
            async for chunk in self.model_client.astream(message):
                if hasattr(chunk, "content") and chunk.content:
                    print(chunk.content, end="", flush=True)
                    assistant_content += chunk.content

            tools_call = await self.parse_tool_use(assistant_content)



