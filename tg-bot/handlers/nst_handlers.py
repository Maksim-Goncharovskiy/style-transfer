import asyncio

from aiogram import Router
from aiogram import F
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext

import logging
import sys

from lexicon import LEXICON_RU
from fsm import FsmNstData

from services import create_user_temp_file, read_user_temp_file, delete_user_temp_dir, get_user_dir_full_path
from services.exceptions import BaseServerError

from ml_services.transfer_style import transfer_style


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.propagate = False

formatter = logging.Formatter(
    '[{asctime}] #{levelname:8} {filename}: {lineno} - {name} - {message}',
    style='{'
)

error_handler = logging.StreamHandler(sys.stderr)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)

class DebugFilter(logging.Filter):
    def filter(self, record):
        return record.levelname == 'DEBUG'

debug_handler = logging.StreamHandler(sys.stdout)
debug_handler.addFilter(DebugFilter())

logger.addHandler(error_handler)
logger.addHandler(debug_handler)


nst_router = Router()



@nst_router.message(Command(commands=["nst"]), StateFilter(default_state))
async def process_nst_request(message: Message, state: FSMContext):
    await message.answer(LEXICON_RU["nst"]["start"])
    await state.set_state(FsmNstData.send_content)



@nst_router.message(StateFilter(FsmNstData.send_content), F.photo)
async def process_content_photo(message: Message, state: FSMContext):
    bot = message.bot

    photo_id = message.photo[-1].file_id
    photo = await bot.get_file(file_id=photo_id)
    downloaded_photo = await bot.download_file(photo.file_path)

    try:
        await create_user_temp_file(user_id=message.from_user.id, img=downloaded_photo.read(), filename="content.jpg")
    except BaseServerError as error:
        logger.error(error)
        await delete_user_temp_dir(user_id=message.from_user.id)
        await message.answer(LEXICON_RU["errors"]["internal_server_error"])
        await state.clear()
    else:
        await message.answer(LEXICON_RU["nst"]["content"])
        await state.set_state(FsmNstData.send_style)



@nst_router.message(StateFilter(FsmNstData.send_content))
async def warn_incorrect_content(message: Message):
    await message.answer(LEXICON_RU["nst"]["bad_photo"])



@nst_router.message(StateFilter(FsmNstData.send_style), F.photo)
async def process_style_photo(message: Message, state: FSMContext):
    bot = message.bot

    photo_id = message.photo[-1].file_id
    photo = await bot.get_file(file_id=photo_id)
    downloaded_photo = await bot.download_file(photo.file_path)

    try:
        await create_user_temp_file(user_id=message.from_user.id, img=downloaded_photo.read(), filename="style.jpg")
    except BaseServerError as error:
        logger.error(error)
        await delete_user_temp_dir(user_id=message.from_user.id)
        await message.answer(LEXICON_RU["errors"]["internal_server_error"])
        await state.clear()
    else:
        await message.answer(LEXICON_RU["nst"]["style"])
        await state.set_state(FsmNstData.send_degree)



@nst_router.message(StateFilter(FsmNstData.send_style))
async def warn_incorrect_style(message: Message):
    await message.answer(LEXICON_RU["nst"]["bad_photo"])



@nst_router.message(StateFilter(FsmNstData.send_degree), lambda x: x.text and x.text.isdigit() and 1 <= int(x.text) <= 5)
async def process_style_transfer_degree(message: Message, state: FSMContext):
    await message.answer(LEXICON_RU["nst"]["degree"])

    try:
        content: bytes = await read_user_temp_file(message.from_user.id, 'content.jpg')
        style: bytes = await read_user_temp_file(message.from_user.id, 'style.jpg')

        # Состояние пользователя переводим в ожидание:
        await state.set_state(FsmNstData.wait_result)

        # получение стилизации, задача добавляется в очередь celery:
        result = transfer_style.delay(content, style, int(message.text))

        # пока задача не выполнена, ждем результат, пользователь должен быть в состоянии ожидания
        while not result.ready():
            await asyncio.sleep(2)

        # сохранение полученной стилизации в папку пользователя
        await create_user_temp_file(user_id=message.from_user.id, img=result.get(), filename='result.jpg')
        user_dir_path = await get_user_dir_full_path(message.from_user.id)
        photo = FSInputFile(user_dir_path + '/result.jpg')

        # отправка ответа
        bot = message.bot
        await bot.send_photo(caption='Вот твоя стилизация:', chat_id=message.chat.id, photo=photo)

    except BaseServerError as error:
        logger.error(error)
        await message.answer(LEXICON_RU["errors"]["internal_server_error"])

    finally:
        await delete_user_temp_dir(user_id=message.from_user.id)
        await state.clear()



@nst_router.message(StateFilter(FsmNstData.send_degree))
async def warn_incorrect_degree(message: Message):
    await message.answer(LEXICON_RU["nst"]["bad_degree"])



@nst_router.message(StateFilter(FsmNstData.wait_result))
async def wait_result(message: Message):
    await message.answer(LEXICON_RU["nst"]["wait"])