from aiogram import Bot, Dispatcher

from settings import TelegramBotSettings, get_settings

from .routers import process_json, start

_bot_settings = get_settings(TelegramBotSettings)


async def create_bot() -> None:
    bot = Bot(_bot_settings.token.get_secret_value(), parse_mode="HTML")
    dp = Dispatcher()

    dp.include_routers(
        start.router,
        process_json.router,
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
