import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from aiogram.fsm.storage.redis import RedisStorage

from redis.asyncio import Redis

import logging
import sys

from config import Config, load_config
from handlers import basic_router, nst_router
from services import create_bot_dir

from keyboards import set_main_menu



async def main():
    logging.info("Загрузка конфигурации...")

    app_config: Config = load_config()

    try:
        await create_bot_dir(app_config.bot.DIR)

    except OSError as error:
        logging.critical(error)

    else:
        logging.info("Подключение Redis")

        redis = Redis(host='localhost', port=6379, db=0)
        # Очистим кэш, потому что при перезапуске бота, некоторые пользователи могут застрять в состоянии ожидания
        await redis.flushall()

        storage = RedisStorage(redis=redis)

        bot = Bot(token=app_config.bot.TOKEN,
                default=DefaultBotProperties(parse_mode=ParseMode.HTML))

        dp = Dispatcher(storage=storage)
        dp.include_router(basic_router)
        dp.include_router(nst_router)

        await set_main_menu(bot)

        await bot.delete_webhook(drop_pending_updates=True)

        logging.info("Запуск бота...")

        await dp.start_polling(bot)



if __name__ == "__main__":
    handler = logging.StreamHandler(sys.stdout)
    logging.basicConfig(level=logging.DEBUG,
                        format='[{asctime}] #{levelname:8} {filename}: {lineno} - {name} - {message}',
                        style='{',
                        handlers=[handler])
    logging.info("Конфигурирование и запуск бота...")

    asyncio.run(main())