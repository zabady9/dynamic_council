import os
from langchain_google_genai import ChatGoogleGenerativeAI

def get_pro_llm():
    """Gemini 1.5 Pro — for deep reasoning, outlining, and validation."""
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite", # Using lite as per previous setup constraints, but ideally gemini-1.5-pro
        google_api_key=os.environ["GOOGLE_API_KEY"],
        temperature=0.2,
        max_retries=2,
    )

def get_flash_llm():
    """Gemini 1.5 Flash — for fast execution, research, and writing."""
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        google_api_key=os.environ["GOOGLE_API_KEY"],
        temperature=0.4,
        max_retries=2,
    )
