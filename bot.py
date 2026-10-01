import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters import CommandStart
from aiogram.types import Message

TOKEN = "8627088338:AAG_WUMeTm6bxII78cdIkSiYhESIQW6lRIQ"

proxy = os.getenv("https_proxy") or os.getenv("HTTPS_PROXY")

session = AiohttpSession(proxy=proxy)
bot = Bot(token=TOKEN, session=session)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    user_id = message.from_user.id
    await message.answer(
        f"مرحباً 👋\n\n"
        f"الـ ID الخاص بك هو:\n"
        f"`{user_id}`"
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
