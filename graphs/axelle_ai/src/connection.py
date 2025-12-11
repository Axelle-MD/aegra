"""Connection module to initialize the LangGraph client."""
from langgraph_sdk import get_client

client = get_client(url="http://localhost:2024")