import os
from agent.chatbot_agent import agent
from service.memory_service import load_history, save_history, reset_history
from dotenv import load_dotenv

USER = os.getenv("USER")

async def run_agent(query: str):
    '''
    Run the query
    '''
    history = load_history(user_id=USER)
    result = await agent.run(query, message_history=history)
    save_history(user_id=USER, messages=result.all_messages())
    return result.output