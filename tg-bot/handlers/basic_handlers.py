from aiogram import F
from aiogram import Router
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from lexicon import LEXICON_RU
from services import delete_user_temp_dir

from keyboards import start_keyboard


basic_router = Router()


@basic_router.message(Command(commands=["start"]), StateFilter(default_state))
async def say_hello(message: Message):
    bot = message.bot
    photo = FSInputFile('./example.jpg')

    await bot.send_photo(message.chat.id, photo, caption=LEXICON_RU["commands"]["start"], reply_markup=start_keyboard)


@basic_router.message(Command(commands=["help"]), StateFilter(default_state))
async def provide_help(message: Message):
    await message.answer(LEXICON_RU["commands"]["help"], reply_markup=start_keyboard)


@basic_router.message(Command(commands=["cancel"]), StateFilter(default_state))
async def handle_useless_cancel(message: Message):
    """
    Обработка команды /cancel вне машины состояний
    """
    await message.answer(LEXICON_RU["commands"]["no_cancel"])


@basic_router.message(Command(commands=["cancel"]), ~StateFilter(default_state))
async def handle_cancel(message: Message, state: FSMContext):
    """
    Обработка команды /cancel от пользователя, находящемся в каком-то из состояний
    """
    await message.answer(LEXICON_RU["commands"]["cancel"])
    await delete_user_temp_dir(user_id=message.from_user.id)
    await state.clear()


@basic_router.message(StateFilter(default_state))
async def answer_any(message: Message):
    await message.answer(text=LEXICON_RU["default"], reply_markup=start_keyboard)