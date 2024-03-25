from aiogram import Bot, Router
from aiogram.types import Message
from ujson import loads

from aggregation import aggregate_salaries
from db import collection

router = Router()


@router.message()
async def process_json(message: Message, bot: Bot):
    try:
        data = loads(message.text)
        results = await aggregate_salaries(
            collection,
            data["dt_from"],
            data["dt_upto"],
            data["group_type"],
        )
        await bot.send_message(message.chat.id, str(results))
    except Exception as e:
        try:
            await bot.send_message(
                message.chat.id,
                """Невалидный запрос. Пример запроса:\n{"dt_from": "2022-09-01T00:00:00", "dt_upto": "2022-12-31T23:59:00", "group_type": "month"}""",
            )
        except Exception as inner_e:
            print(f"Ошибка при отправке сообщения: {str(inner_e)}")
