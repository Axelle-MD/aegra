
from typing import Optional, Dict, List
from langgraph_sdk.schema import Thread
from graphs.axelle_ai.src.connection import client
from langchain_core.messages import AIMessage
async def get_user_threads(user_id:str) -> Optional[List[Thread]]:
    """Retrieve threads for a given user ID
    Args:
        user_id (str): The ID of the user.
    Returns:
        Optional[List[Dict]]: A list of threads for the user, or None if no threads are found.
    """
    threads = await client.threads.search(
        metadata={"user_id": user_id}
    )
    return threads

async def create_thread(user_id: str) -> Thread:
    """Create a thread for user with ID 'user_id'.
    Args:
        user_id (str): The ID of the user.
    Returns:
        Thread: The created thread.
    """
    thread = await client.threads.create(metadata={"user_id": user_id, "title": None})
    return thread

async def get_thread(thread_id: str) -> Thread:
    """Retrieve a thread by its ID.
    Args:
        thread_id (str): The ID of the thread.
    Returns:
        Optional[Thread]: The thread if found, otherwise None.
    """
    thread = await client.threads.get(thread_id=thread_id)
    return thread

async def format_user_threads_to_include_only_title(user_id: str) -> List[Dict[str, str]]:
    threads: Optional[List[Thread]] = await get_user_threads(user_id)
    if not threads:
        return []
    return [{
        "thread_id": t["thread_id"],
        "title": (t.get("metadata") or {}).get("title", "New Chat"),
    } for t in threads]


async def generate_title(messages: List[Dict[str, str]]) -> str:
    """Generate a concise title from the first user message"""
    # Use a fast model to generate title
    print("Generating title...")
    from graphs.axelle_ai.src.config import llama3p3_70b_versatile
    from langchain.messages import SystemMessage, HumanMessage
    first_message = messages[0]["content"]
    print(f"First message: {first_message}")
    response : AIMessage = await llama3p3_70b_versatile.ainvoke([SystemMessage(content="Generate a short 3-5 word title for this conversation. Be concise."), HumanMessage(content=first_message)])
    from typing import cast
    return cast(str, response.content)


async def update_thread_title(thread_id: str, messages: List[Dict[str, str]]):
    """Update thread title by generating from messages."""
    print(f"Generating title for thread {thread_id}...")
    try:
        title = await generate_title(messages)
        print(f"Generated title: '{title}'")
        await client.threads.update(thread_id, metadata={"title": title})
        print(f"✅ Thread title updated successfully")
        return title
    except Exception as e:
        print(f"Failed to update thread title: {e}")
        return None



