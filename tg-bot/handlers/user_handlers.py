from aiogram import Router
from aiogram.types import Message
from aiogram.filters import StateFilter
from aiogram.fsm.state import default_state
from lexicon import LEXICON_RU

from keyboards import start_keyboard


user_router = Router()

@user_router.message(StateFilter(default_state))
async def answer_any(message: Message):
    await message.answer(text=LEXICON_RU["default"], reply_markup=start_keyboard)