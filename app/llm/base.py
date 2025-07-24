import os
from app.config import llm_settings

os.environ["LANGSMITH_TRACING"] = llm_settings.LANGSMITH_TRACING
os.environ["LANGSMITH_ENDPOINT"] = llm_settings.LANGSMITH_ENDPOINT
os.environ["LANGSMITH_API_KEY"] = llm_settings.LANGSMITH_API_KEY
os.environ["LANGSMITH_PROJECT"] = llm_settings.LANGSMITH_PROJECT


from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=llm_settings.GEMINI_API_KEY
)
