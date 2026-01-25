import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("No OPENAI_API_KEY in .env. Add it and run again!")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

user_question = "Using simple words explain: what is artificial intelligence?"

response = llm.invoke([HumanMessage(content=user_question)])

print("LLM Response:\n", response.content)