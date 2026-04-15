import asyncio
import os
from core.logging import get_logger
from service.telegram_service import dp, make_bot

logger = get_logger(__name__)

def run():
    '''
    Run the polling service [env=local]
    '''
    token: str = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error(f'[TELEBOT][POLLING] token not set.')

    bot = make_bot(token)
    logger.info(f'[TELEBOT][POLLING] starting on polling mode')
    asyncio.run(dp.start_polling(bot))