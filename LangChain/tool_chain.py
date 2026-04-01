import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.tools import tool
from openai import embeddings

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

@tool(
    "calculator",
    description="Calculate math expression ('0123456789+-*/(). ')"
)
def safe_calculate(expression: str) -> str:
    allowed_chars = "0123456789+-*/(). "
    if not all(ch in allowed_chars for ch in expression):
        return "Error: allowed chars '0123456789+-*/(). '"
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return result
    except Exception as e:
        return f"Error: {e}"


from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

with open("data/faq.txt", "r", encoding="utf-8") as f:
    faq_text = f.read()
splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
docs = splitter.create_documents([faq_text])

embeddings = OpenAIEmbeddings()

vector_store = FAISS.from_documents(docs, embeddings)

@tool
def search_faq(query: str) -> str:
    """Question/answer Faq"""
    try:
        # result = vector_store.search(query)
        result = vector_store.similarity_search(query, k=1)
        if not result:
            return "Nothing found in FAQ"
        return result[0].page_content

    except Exception as e:
        return f"Error: {e}"

@tool
def weather_api(city: str) -> str:
    """Provides data on weather in secific cities"""
    data = {
        "Kharkiv": "Sunny, 0..+2C",
        "Kyiv": "Cloudy, -1..+1C, windy",
        "Lviv": "Rainy, +2..+3C"
    }
    return data.get(
        city,
        f"No data found. Try one of these cities: {", ".join(list(data.keys()))}"
    )




from langchain.agents import create_agent


tools = [safe_calculate, search_faq, weather_api]
prompt = (
    "You have access to a tool that retrieves context from a blog post. "
    "Use the tool to help answer user queries."
    "Use weather_api tool to retrieve weather information."
    "Use search_faq tool to retrieve the most relevant FAQ/blog content using semantic search."
    "The search_faq tool returns relevant context text."
    "Use that context to generate the final answer."
    "If the tool returns Nothing Found у FAQ, tell the user that the information was not found."
    "Do NOT invent information that is not in the retrieved content."
    "If the question does not require FAQ data, answer normally."
)
# agent = create_agent(model, tools, system_prompt=prompt)
agent = create_agent(
    model = llm,
    tools = tools,
    system_prompt = prompt,
    debug = True
)

def get_output(result: dict) -> str:
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

if __name__ == "__main__":
    print("\nCalculator")
    result = agent.invoke({"messages": [{"role": "user", "content": "Calculate: (2+3)*4-5"}]})
    print(get_output(result))

    print("\nWeather")
    result = agent.invoke({"messages": [{"role": "user", "content": "What's the weather in Kharkiv"}]})
    print(get_output(result))