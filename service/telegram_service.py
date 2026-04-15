from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, BufferedInputFile
from io import BytesIO
from core.logging import get_logger
from service.agent_service import run_agent
from service.voice_service import transcribe, synthesize

logger = get_logger(__name__)

dp = Dispatcher()

def make_bot(token: str):
    '''
    Create the bot
    '''
    return Bot(token=token)

@dp.message(F.text)
async def on_message(message: Message):
    '''
    Send the message
    '''
    user_id: str = str(message.from_user.id)
    text: str = message.text if message.text else ''

    if not text:
        logger.info(f'[TELEBOT][MSG] no message from {user_id}, ignoring.')

    logger.info(f'[TELEBOT][MSG] message from {user_id}: {text}')

    try:
        reply = await run_agent(query=text)
    except Exception as e:
        logger.exception(f'[TELEBOT][MSG] message failed for user: {user_id}, error: {e}')
        await message.answer('Something went wrong, please Try again.')
        return

    await message.answer(reply)

@dp.message(F.voice)
async def on_voice(message: Message) -> None:
    user_id = str(message.from_user.id)
    chat_id = message.chat.id

    logger.info("[TELEBOT][VOICE] voice msg from %s, duration=%ss",
                user_id, message.voice.duration)

    # 1. Download the voice file from Telegram
    file = await message.bot.get_file(message.voice.file_id)
    buf = BytesIO()
    await message.bot.download_file(file.file_path, destination=buf)
    audio_bytes = buf.getvalue()

    # 2. Transcribe
    try:
        text = await transcribe(audio_bytes)
    except Exception:
        logger.exception("[TELEBOT][VOICE] transcription failed")
        await message.answer("Couldn't understand the audio, try again?")
        return

    if not text:
        await message.answer("I didn't catch anything in that voice note.")
        return

    # 3. Run the agent on the transcribed text
    try:
        reply = await run_agent(query=text)
    except Exception:
        logger.exception("[TELEBOT][VOICE] agent failed for %s", user_id)
        await message.answer("Something went wrong, please try again.")
        return

    # 4. Synthesize the reply and send as voice
    try:
        audio_reply = await synthesize(reply)
    except Exception:
        logger.exception("[TELEBOT][VOICE] synthesis failed, falling back to text")
        await message.answer(reply)
        return

    voice_file = BufferedInputFile(audio_reply, filename="reply.ogg")
    await message.answer_voice(voice_file)