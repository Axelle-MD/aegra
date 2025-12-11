from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.chat_models import init_chat_model

load_dotenv(override=True)

llama3p3_70b_versatile = init_chat_model(
    "groq:llama-3.3-70b-versatile",
    temperature=0.5,
    timeout=10,
    max_tokens=1000
)

gpt_oss_20b = ChatGroq(model="openai/gpt-oss-20b", temperature=0)
gpt_oss_120b = ChatGroq(model="openai/gpt-oss-120b", temperature=0)