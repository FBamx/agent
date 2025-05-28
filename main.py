import asyncio
from mcp_llm import LLMClient
from mcp_client import MCPServer


async def main():
    llm = LLMClient(model="deepseek-chat", base_url="https://api.deepseek.com",
                    api_key="sk-b75a12605fdb4dd48d2b2e286425c953")

    llm.system_prompt = "你是一个生活小助手"

    llm.add_mcp_server(MCPServer(
        id="weather",
        name="weather",
        command="uv",
        args=["run", "./mcp_server/server.py"]
    ))

    await llm.get_mcp_tools()

    print("AI助手已启动, 输入 'quit' 退出, 'history' 显示历史消息, 'clear' 清空历史消息")

    while True:
        user_input = input("\n\n你: ").strip()
        if user_input.lower() == "quit":
            print("退出AI助手")
            break
        elif user_input.lower() == "history":
            pass
        elif user_input.lower() == "clear":
            pass
        else:
            print("\nAI助手: ", end="")
            await llm.chat(user_input)


if __name__ == "__main__":
    asyncio.run(main())
