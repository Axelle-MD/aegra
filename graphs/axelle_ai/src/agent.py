from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.chat_models import init_chat_model
from graphs.axelle_ai.src.config import llama3p3_70b_versatile, gpt_oss_20b, gpt_oss_120b

load_dotenv(override=True)

SYSTEM_PROMPT = """You are an expert health assistant.

You have access to two tools:

- get_date: use this to get the current date
- internet_search: use this to search the internet for information you need
- get_user_location: use to get user's current location

If a user ask a question and you don't have enough context to answer the question, use the internet_search tool, prioritize recent information. get_date tool will help you know know the current date"""

from tavily import TavilyClient
import os
tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

from dataclasses import dataclass
from langchain.tools import tool, ToolRuntime
from typing import Literal

# ---------- Trusted medical domains ----------
TRUSTED_DOMAINS = [
    "who.int", "cdc.gov", "nih.gov", "ncbi.nlm.nih.gov",
    "ema.europa.eu", "ema.eu", "fda.gov",
    "nice.org.uk", "bmj.com", "nejm.org", "thelancet.com",
    "mayoclinic.org", "clevelandclinic.org", "uptodate.com",
    "unicef.org", "unfpa.org"
]

@tool
def get_date():
    """Get the current date."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d")

@tool
# Search tool to use to do research
def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance" ] = "general",
    include_raw_content: bool = False,
):
    """Run a web search"""
    search_docs = tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
        #add trusted domains
        #trusted_domains=TRUSTED_DOMAINS,
    )
    return search_docs

@dataclass
class Context:
    """Custom runtime context schema."""
    user_id: str = "1"  # Default user_id

@tool
def get_user_location(runtime: ToolRuntime[Context]) -> str:
    """Retrieve user information based on user ID."""
    user_id = runtime.context.user_id
    return "Ghana" if user_id == "1" else "Europe"

from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()

from langchain.agents import create_agent
agent = create_agent(
    model=llama3p3_70b_versatile,
    system_prompt=SYSTEM_PROMPT,
    tools=[get_date, internet_search, get_user_location],
    context_schema=Context,
    #response_format=ResponseFormat,
    #checkpointer=checkpointer
)