import asyncio
from llm import LLM


def main():
    llm = LLM(model="deepseek-chat", base_url="https://api.deepseek.com",
              api_key="sk-b75a12605fdb4dd48d2b2e286425c953")
    llm.set_system_prompt("你是一个留学小助手, 解答一切关于留学的事情, 不要瞎编, 不要回答任何敏感话题")

    print("AI助手已启动, 输入 'quit' 退出, 'history' 显示历史消息, 'clear' 清空历史消息")

    while True:
        user_input = input("\n你: ").strip()
        if user_input.lower() == "quit":
            print("退出AI助手")
            break
        elif user_input.lower() == "history":
            conversation_history = llm.conversation_history()
            for i, history in enumerate(conversation_history[:], 1):
                print(f"第{i}轮对话:")
                print(f"用户: {history['human']}\n")
                print(f"AI: {history['ai']}\n")
        elif user_input.lower() == "clear":
            llm.clear_conversation_history()
        else:
            print("\nAI助手: ", end="")
            llm.chat(user_input)


if __name__ == "__main__":
    main()
