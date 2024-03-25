import asyncio

import dotenv

from telegram_bot import create_bot

if __name__ == "__main__":
    dotenv.load_dotenv(".env")
    asyncio.run(create_bot())
