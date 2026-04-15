import os
from aiogram import Bot
from aiogram.types import Update
from fastapi import FastAPI, Request
from service.telegram_service import dp, make_bot
from core.logging import get_logger

logger = get_logger(__name__)

app = FastAPI()
bot: Bot


@app.lifespan('startup')
async def startup():
    global bot
    token: str = os.getenv('TELEGRAM_BOT_TOKEN')
    webhook_url: str = os.getenv('WEBHOOK_URL', '')
    bot = make_bot(token=token)

    await bot.set_webhook(webhook_url=webhook_url)

@app.post('/webhook')
async def webhook(request: Request):
    update = Update.model_validate(await request.json())
    await dp.feed_update(bot, update)
    return {'status': 'ok'}

def run():
    import uvicorn
    logger.info(f'[TELEBOT][WEBHOOK] starting on webhook mode')
    uvicorn.run(app, host='0.0.0.0', port=8080)