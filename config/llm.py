
import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables from your .env file
load_dotenv()

def get_llm():
    """Returns the configured OpenAI LLM instance."""
    return ChatOpenAI(
        model="gpt-5.4-mini-2026-03-17", 
        temperature=0.7,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    ) 