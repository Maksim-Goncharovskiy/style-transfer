import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from aiogram.fsm.storage.redis import RedisStorage

from redis.asyncio import Redis

from config import Config, load_config
from handlers import basic_router, nst_router
import logging


async def main():
    logging.info("Загрузка конфигурации...")

    app_config: Config = load_config()

    redis = Redis(host='localhost', port=6379, db=0)
    storage = RedisStorage(redis=redis)

    bot = Bot(token=app_config.bot.TOKEN,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp = Dispatcher(storage=storage)
    dp.include_router(basic_router)
    dp.include_router(nst_router)

    await bot.delete_webhook(drop_pending_updates=True)

    logging.info("Запуск бота...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='[{asctime}] #{levelname:8} {filename}: {lineno} - {name} - {message}',
                        style='{')
    logging.info("Конфигурирование и запуск бота...")

    asyncio.run(main())