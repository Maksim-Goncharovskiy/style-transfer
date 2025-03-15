import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import Config, load_config
from handlers import basic_router
import logging


async def main():
    logging.info("Загрузка конфигурации...")

    app_config: Config = load_config()

    bot = Bot(token=app_config.bot.TOKEN,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp = Dispatcher()
    dp.include_router(basic_router)

    await bot.delete_webhook(drop_pending_updates=True)

    logging.info("Запуск бота...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='[{asctime}] #{levelname:8} {filename}: {lineno} - {name} - {message}',
                        style='{')
    logging.info("Конфигурирование и запуск бота...")

    asyncio.run(main())