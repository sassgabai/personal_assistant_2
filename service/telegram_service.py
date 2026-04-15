from aiogram import Bot, Dispatcher
from aiogram.types import Message
from core.logging import get_logger
from service.agent_service import run_agent

logger = get_logger(__name__)

dp = Dispatcher()

def make_bot(token: str):
    '''
    Create the bot
    '''
    return Bot(token=token)

@dp.message()
async def on_message(message: Message):
    '''
    Send the message
    '''
    user_id: str = str(message.from_user.id)
    text: str = message.text if message.text else ''

    lan: float = message.location.latitude
    lon: float = message.location.longitude

    if not text:
        logger.info(f'[TELEBOT][MSG] no message from {user_id}, ignoring.')

    logger.info(f'[TELEBOT][MSG] message from {user_id}: {text}')
    logger.info(f'[TELEBOT][MSG] lan: {lan}, lon: {lon}')

    try:
        reply = await run_agent(query=text)
    except Exception as e:
        logger.exception(f'[TELEBOT][MSG] message failed for user: {user_id}, error: {e}')
        await message.answer('Something went wrong, please Try again.')
        return

    await message.answer(reply)