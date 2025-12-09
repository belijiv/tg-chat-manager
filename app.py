import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from database import Database
from controllers.group_controller import GroupController
from controllers.admin_controller import AdminController

from config import config

logging.basicConfig(level=logging.INFO)


async def main():
    try:
        bot = Bot(token=config.BOT_TOKEN)
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)

        db = Database()

        admin_controller = AdminController(bot, db)
        group_controller = GroupController(bot, db)

        admin_controller.register_handlers(dp)
        group_controller.register_handlers(dp)

        print("🤖 Бот запущен и готов к работе!")
        await dp.start_polling(bot)

    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())