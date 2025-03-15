import os
import shutil
from aiogram import Router
from aiogram import F
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from lexicon import LEXICON_RU
from fsm import FsmNstData


nst_router = Router()


@nst_router.message(Command(commands=["nst"]), StateFilter(default_state))
async def process_nst_request(message: Message, state: FSMContext):
    await message.answer(LEXICON_RU["commands"]["nst"])
    await state.set_state(FsmNstData.send_content)


@nst_router.message(StateFilter(FsmNstData.send_content), F.photo)
async def process_content_photo(message: Message, state: FSMContext):
    bot_tmp_dir = "/tg-bot/temp"
    user_tmp_dir = str(message.from_user.id)
    path = os.path.join(bot_tmp_dir, user_tmp_dir)
    os.mkdir(path)

    bot = message.bot

    photo_id = message.photo[-1].file_id
    photo = await bot.get_file(file_id=photo_id)
    downloaded_photo = await bot.download_file(photo.file_path)

    with open(f"{path}/content.jpg", "wb") as f:
        f.write(downloaded_photo.read())

    await message.answer("Ты отправил фото контента! Молодца! Теперь отправь фото стиля!")
    await state.set_state(FsmNstData.send_style)


@nst_router.message(StateFilter(FsmNstData.send_content))
async def warn_incorrect_content(message: Message):
    await message.answer("Бро, мне нужно фото. Если передумал, отправляй /cancel")


@nst_router.message(StateFilter(FsmNstData.send_style), F.photo)
async def process_style_photo(message: Message, state: FSMContext):
    bot_tmp_dir = "/tg-bot/temp"
    user_tmp_dir = str(message.from_user.id)
    path = os.path.join(bot_tmp_dir, user_tmp_dir)
    #
    os.mkdir(path)

    bot = message.bot

    photo_id = message.photo[-1].file_id
    photo = await bot.get_file(file_id=photo_id)
    downloaded_photo = await bot.download_file(photo.file_path)

    with open(f"{path}/style.jpg", "wb") as f:
        f.write(downloaded_photo.read())

    await message.answer("Ты отправил фото стиля! Молодца! Теперь выбери степень переноса стиля: ")
    await state.set_state(FsmNstData.send_degree)


@nst_router.message(StateFilter(FsmNstData.send_style))
async def warn_incorrect_style(message: Message):
    await message.answer("Бро, мне нужно фото. Если передумал, отправляй /cancel")


@nst_router.message(StateFilter(FsmNstData.send_degree), lambda x: x.text and x.text.isdigit() and 1 <= int(x.text) <= 5)
async def process_style_transfer_degree(message: Message, state: FSMContext):
    await message.answer("Отлично, самое время стилизовать...")
    # ... здесь код получения стилизации
    await message.answer("Вот стилизация: ")
    # ... удаление данных
    bot_tmp_dir = "/tg-bot/temp"
    user_tmp_dir = str(message.from_user.id)
    path = os.path.join(bot_tmp_dir, user_tmp_dir)
    shutil.rmtree(path)

    await state.clear()


@nst_router.message(StateFilter(FsmNstData.send_degree))
async def warn_incorrect_degree(message: Message):
    await message.answer("Мне нужно число от 1 до 5. Передумал? Отправляй /cancel.")