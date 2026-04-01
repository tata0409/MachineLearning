import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
agent = create_agent(
    model=llm,
    tools=[],
    system_prompt="You're a friendly assistant, answering simply but effectively",
    debug=False
)


def get_output(result: dict)-> str:
    messages = result.get("messages", [])
    for msg in reversed(messages):
        content = getattr(msg, "content", None)
        tool_calls = getattr(msg, "tool_calls", None) or []
        if content and not tool_calls:
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                return "".join(
                    c.get("text", str(c)) if isinstance(c, dict) else str(c) for c in content
                )
    return ""


chat_messages = []


def chat(user_input: str, agent=agent) -> str:
    chat_messages.append({"role": "user", "content": user_input})

    result = agent.invoke({"messages": chat_messages})

    chat_messages.clear()
    chat_messages.extend(result["messages"])

    return get_output(result)

def run_demo():
    print("Answer 1:", chat("Hello! My name's Tetiana"))
    print("Answer 2:", chat("Remember, I like programming"))
    print("Answer 3:", chat("Remind me what's my name and what do I like?"))

def run_interactive(agent=agent):
    while True:
        user_input = input("User: ")

        if user_input.lower() in ["exit"]:
            break

        response = chat(user_input, agent=agent)
        print("Agent:", response)


if __name__ == "__main__":
    mode = input("Demo or interactive: ").strip().lower()
    if mode == "d":
        run_demo()
    elif mode == "i":
        run_interactive()

