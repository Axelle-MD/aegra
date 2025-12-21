from dotenv import load_dotenv
from graphs.axelle_ai.src.config import llama3p3_70b_versatile, gpt_oss_20b, gpt_oss_120b
from graphs.axelle_ai.src.tools import get_date, internet_search, get_user_location,search_medical_docs

from graphs.axelle_ai.src.prompts import SYSTEM_PROMPT

from graphs.axelle_ai.src.contexts import Context


from langchain.agents import create_agent
agent = create_agent(
    model=llama3p3_70b_versatile,
    system_prompt=SYSTEM_PROMPT,
    tools=[get_date, internet_search, get_user_location, search_medical_docs],
    context_schema=Context,
)