from io import BytesIO
from openai import AsyncOpenAI
from core.logging import get_logger

logger = get_logger(__name__)
client = AsyncOpenAI()

async def transcribe(audio: bytes, filename: str = 'voice.ogg'):
    '''
    Transcribe from speech to text with Whisper-1
    '''
    audio = BytesIO(audio)
    audio.name = filename

    result = await client.audio.transcriptions.create(
        model='whisper-1',
        file=audio
    )
    text = result.text.strip()
    logger.info(f'[TRANSCRIBE] message transcribed: {text}')
    return text


async def synthesize(text: str, voice: str ='echo'):
    '''
    Synthesize from text to speed
    '''
    response = await client.audio.speech.create(
        model='tts-1',
        voice=voice,
        input=text,
        response_format='opus'
    )

    audio = response.read()
    logger.info(f'[SYNTHESIZE] synthesized: {text}')
    return audio
