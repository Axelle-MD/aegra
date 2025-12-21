from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.chat_models import init_chat_model
from tavily import TavilyClient

load_dotenv(override=True)

llama3p3_70b_versatile = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.5,
    timeout=10,
    max_tokens=1000
)

gpt_oss_20b = ChatGroq(model="openai/gpt-oss-20b", temperature=0)
gpt_oss_120b = ChatGroq(model="openai/gpt-oss-120b", temperature=0)

import os
tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

# ---------- Trusted medical domains ----------
TRUSTED_DOMAINS = [
    "who.int", "cdc.gov", "nih.gov", "ncbi.nlm.nih.gov",
    "ema.europa.eu", "ema.eu", "fda.gov",
    "nice.org.uk", "bmj.com", "nejm.org", "thelancet.com",
    "mayoclinic.org", "clevelandclinic.org", "uptodate.com",
    "unicef.org", "unfpa.org"
]


# ---------- Weaviate client and embeddings ----------
from langchain_openai import OpenAIEmbeddings
EMBEDDING_MODEL = OpenAIEmbeddings()