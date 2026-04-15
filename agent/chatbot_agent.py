import os
from pydantic_ai import Agent
from dotenv import load_dotenv
from prompt.system_prompt import get_system_prompt
from agent.tools import weather, calendar, datetime
from core.logging import get_logger

load_dotenv()

logger = get_logger(__name__)

ANTHROPIC_MODEL = os.getenv('ANTHROPIC_MODEL_NAME')
SYSTEM_PROMPT = get_system_prompt()

agent = Agent(
    model=ANTHROPIC_MODEL,
    system_prompt=
    f'''
        You are a personal assistant called Divad and you will be chatting with your owner over Telegram.
        You are nice, cheerful and very helpful.

        when the user asks relative time like "tomorrow", "next week", "2 days ago" and etc- resolve
        them yourself using the current datetime implied.
        Do NOT ask for a specific date- you got everything you have
    '''
)

# @agent.system_prompt(dynamic=True)
# def get_current_datetime():
#     current_datetime = datetime.now().isoformat()
#     print(f'[LLM] Current datetime: {current_datetime}')
#     return f'current datetime: {current_datetime}'

weather.register(agent)
calendar.register(agent)
datetime.register(agent)
