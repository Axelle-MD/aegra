from fastapi import FastAPI
from graphs.axelle_ai.src.utils import get_user_threads, create_thread, get_thread

app = FastAPI()

@app.get("/threads/{user_id}")
async def read_user_threads(user_id: str):
    threads = await get_user_threads(user_id)
    return threads

@app.post("/thread/store")
async def create_new_thread(user_id: str):
    thread = await create_thread(user_id)
    return thread

@app.get("/thread/{thread_id}")
async def get_thread_by_id(thread_id: str):
    thread = await get_thread(thread_id)
    return thread

