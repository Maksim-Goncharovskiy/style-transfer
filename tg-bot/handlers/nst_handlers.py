import asyncio

from aiogram import Router
from aiogram import F
from aiogram.types import Message, FSInputFile, CallbackQuery
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
from keyboards import start_keyboard, degree_keyboard


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
    """
    Обработка команды /nst в дефолтном состоянии.
    Переход в состояние ожидания фото-контента.
    """
    await message.answer(LEXICON_RU["nst"]["start"])
    await state.set_state(FsmNstData.send_content)


@nst_router.callback_query(F.data == 'start_nst', StateFilter(default_state))
async def process_start_button_pressed(callback: CallbackQuery, state: FSMContext):
    """
    То же самое, что и хэндлер process_nst_request, только обрабатывается нажатие кнопки.
    """
    await callback.message.answer(LEXICON_RU["nst"]["start"])
    await state.set_state(FsmNstData.send_content)


@nst_router.callback_query(F.data == 'start_nst', ~StateFilter(default_state))
async def warn_start_button_bad_pressed(callback: CallbackQuery, state: FSMContext):
    """
    Обработка ситуации нажатия кнопки в невалидном для этого состоянии (повторное нажатие).
    """
    await callback.answer(LEXICON_RU["nst"]["bad_button"])


@nst_router.message(StateFilter(FsmNstData.send_content), F.photo)
async def process_content_photo(message: Message, state: FSMContext):
    """
    Обработка полученного фото-контента.
    Скачивание и сохранение на сервер во временную директорию для пользователя.
    """
    bot = message.bot

    photo_id = message.photo[-1].file_id
    photo = await bot.get_file(file_id=photo_id)
    downloaded_photo = await bot.download_file(photo.file_path)

    # При сохранении файла может возникнуть исключительная ситуация, если вдруг файловая структура бота была нарушена
    # (удаление папки бота/пользователя). Обрабатываем исключение, выводим лог.
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
        await message.answer(LEXICON_RU["nst"]["style"], reply_markup=degree_keyboard)
        await state.set_state(FsmNstData.send_degree)



@nst_router.message(StateFilter(FsmNstData.send_style))
async def warn_incorrect_style(message: Message):
    await message.answer(LEXICON_RU["nst"]["bad_photo"])



@nst_router.callback_query(StateFilter(FsmNstData.send_degree), F.data.in_([str(i) for i in range(1, 6)]))
async def process_style_transfer_degree(callback: CallbackQuery, state: FSMContext):
    """
    Обработка степени стилизации. Запуск процедуры получения стилизации.
    """
    user_id = callback.from_user.id
    await callback.message.answer(LEXICON_RU["nst"]["degree"])

    try:
        content: bytes = await read_user_temp_file(user_id=user_id, filename='content.jpg')
        style: bytes = await read_user_temp_file(user_id=user_id, filename='style.jpg')

        # Состояние пользователя переводим в ожидание:
        await state.set_state(FsmNstData.wait_result)

        logger.debug(f"Стилизация для {callback.from_user.first_name} с id {user_id} в очереди.")
        # получение стилизации, задача добавляется в очередь celery:
        result = transfer_style.delay(content, style, int(callback.data))

        # пока задача не выполнена, ждем результат, пользователь должен быть в состоянии ожидания
        while not result.ready():
            await asyncio.sleep(2)

        logger.debug(f"Стилизация для {callback.from_user.first_name} с id {user_id} завершена.")

        # сохранение полученной стилизации в папку пользователя
        await create_user_temp_file(user_id=user_id, img=result.get(), filename='result.jpg')
        user_dir_path = await get_user_dir_full_path(user_id=user_id)
        photo = FSInputFile(user_dir_path + '/result.jpg')

        # отправка ответа
        bot = callback.message.bot
        await bot.send_photo(caption=LEXICON_RU["nst"]["done"], chat_id=callback.message.chat.id, photo=photo,
                             reply_markup=start_keyboard)

    except BaseServerError as error:
        logger.error(error)
        await callback.message.answer(LEXICON_RU["errors"]["internal_server_error"])

    finally:
        await delete_user_temp_dir(user_id=user_id)
        await state.clear()


@nst_router.callback_query(~StateFilter(FsmNstData.send_degree), F.data.in_([str(i) for i in range(1, 6)]))
async def warn_degree_button_bad_pressed(callback: CallbackQuery):
    await callback.answer(LEXICON_RU["nst"]["bad_button"])


@nst_router.message(StateFilter(FsmNstData.send_degree))
async def warn_incorrect_degree(message: Message):
    await message.answer(LEXICON_RU["nst"]["bad_degree"])


@nst_router.message(StateFilter(FsmNstData.wait_result))
async def wait_result(message: Message):
    await message.answer(LEXICON_RU["nst"]["wait"])