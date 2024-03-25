from aiogram import Bot, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def start(message: Message, bot: Bot):
    user_names = f"{message.from_user.first_name} {message.from_user.last_name}"
    user_link = f"<a href='tg://user?id={message.from_user.id}'>{user_names}</a>"
    await bot.send_message(message.chat.id, f"Hi {user_link}!")
