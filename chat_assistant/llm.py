from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, AIMessage, HumanMessage


class LLM:
    def __init__(self, model: str, base_url: str, api_key: str):
        self._llm = ChatOpenAI(
            model=model,
            base_url=base_url,
            api_key=api_key
        )
        self._system_prompt = None
        self._conversation_history = []

    @property
    def system_prompt(self):
        return self._system_prompt

    def conversation_history(self):
        return self._conversation_history

    def set_system_prompt(self, system_prompt: str):
        self._system_prompt = SystemMessage(content=system_prompt)

    def clear_conversation_history(self):
        self._conversation_history = []

    def chat(self, user_message: str, stream=True):
        message = []

        # 添加系统提示词
        if self._system_prompt:
            message.append(self._system_prompt)

        # 添加会话历史
        for history in self._conversation_history[-5:]:
            message.append(HumanMessage(content=history["human"]))
            message.append(AIMessage(content=history["ai"]))

        # 添加用户输入
        message.append(HumanMessage(content=user_message))
        resp_content = ""
        if stream:
            for chunk in self._llm.stream(message):
                if chunk.content:
                    print(chunk.content, end="", flush=True)
                    resp_content += chunk.content
            print()
        else:
            resp_content = self._llm.invoke(message).content
            print(resp_content)

        # 记录会话历史
        self._conversation_history.append({
            "human": user_message,
            "ai": resp_content
        })








