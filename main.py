import asyncio
import logging

from config_data.config import config
from aiogram import Bot, Dispatcher

from database.database import create_tables
from handlers.converter import router as calculator_router
from handlers.menu import router as menu_router
from handlers.settings import router as settings_router
from handlers.view_currency import router as view_cur_router
from handlers.history import router as about_router
from handlers.payment import router as payment_router


async def main():
    #logging.basicConfig(level=logging.DEBUG)
    bot = Bot(token=config.bot_token)
    dp = Dispatcher()

    await create_tables()

    dp.include_router(calculator_router)
    dp.include_router(settings_router)
    dp.include_router(menu_router)
    dp.include_router(view_cur_router)
    dp.include_router(about_router)
    dp.include_router(payment_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

asyncio.run(main())