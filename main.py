import os
from dotenv import load_dotenv
from service.agent_service import run_agent
from core.logging import setup_logger

load_dotenv()


def main():
    setup_logger()
    ENV = os.getenv('ENV')

    if ENV == 'local':
        from core.telegram_bot.polling import run
        run()

    elif ENV == 'remote':
        from core.telegram_bot.webhook import run
        run()

    else:
        raise ValueError(f'[MAIN] unknown ENV: {ENV}')


if __name__ == '__main__':
    main()
