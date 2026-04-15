import os
from pydantic_ai import Agent
from dotenv import load_dotenv
from prompt.system_prompt import get_system_prompt

load_dotenv()

ANTHROPIC_MODEL = os.getenv('ANTHROPIC_MODEL_NAME')
SYSTEM_PROMPT = get_system_prompt()

agent = Agent(
    model=ANTHROPIC_MODEL,
    system_prompt=SYSTEM_PROMPT
)