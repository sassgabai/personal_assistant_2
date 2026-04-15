import os
import httpx
from core.logging import get_logger
from pydantic_ai import Agent
from dotenv import load_dotenv

load_dotenv()
logger = get_logger(__name__)

LAT = os.getenv("LAT")
LON = os.getenv("LON")
TOMORROW_URL = os.getenv('TOMORROW_URL')

WEATHER_CODES: dict = {
    1000: "clear",
    1100: "mostly clear",
    1101: "partly cloudy",
    1102: "mostly cloudy",
    1001: "cloudy",
    2000: "fog",
    2100: "light fog",
    4000: "drizzle",
    4001: "rain",
    4200: "light rain",
    4201: "heavy rain",
    5000: "snow",
    5001: "flurries",
    5100: "light snow",
    5101: "heavy snow",
    6000: "freezing drizzle",
    6200: "light freezing rain",
    6201: "heavy freezing rain",
    7000: "ice pellets",
    7101: "heavy ice pellets",
    7102: "light ice pellets",
    8000: "thunderstorm",
}

def register(agent: Agent):
    @agent.tool_plain
    async def get_weather():
        '''
        Get the current weather for the given lon and lat, Israel
        '''
        api_key: str = os.getenv("TOMMOROW_API_KEY")

        if not api_key:
            logger.error(f'[WEATHER] did not receive API key')
            return "Weather service is unreachable"

        params: dict = {
            'location': f'{LAT},{LON}',
            'units': 'metric',
            'apikey': api_key
        }

        async with httpx.AsyncClient(timeout=10) as client:
            try:
                response = await client.get(TOMORROW_URL, params=params)
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                logger.error(f'[WEATHER] failed fetching weather info: {e}')
                return 'Error with weather service'

        data: dict = response.json()['data']['values']
        logger.info(f'[WEATHER] {data}')

        temp = data['temperature']
        feels = data['temperatureApparent']
        rain_probability = data['precipitationProbability']

        relevant_info: str = f'''
            The temperature is {temp} Celsius and feels like {feels} Celsius,
            Rain probability is {rain_probability}%
        '''

        return relevant_info



