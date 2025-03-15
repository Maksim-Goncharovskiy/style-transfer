from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from lexicon import LEXICON_RU


basic_router = Router()


@basic_router.message(Command(commands=["start"]), StateFilter(default_state))
async def say_hello(message: Message):
    await message.answer(LEXICON_RU["commands"]["start"])


@basic_router.message(Command(commands=["help"]), StateFilter(default_state))
async def provide_help(message: Message):
    await message.answer(LEXICON_RU["commands"]["help"])


@basic_router.message(Command(commands=["cancel"]), StateFilter(default_state))
async def handle_useless_cancel(message: Message):
    await message.answer(LEXICON_RU["commands"]["no_cancel"])


@basic_router.message(Command(commands=["cancel"]), ~StateFilter(default_state))
async def handle_useless_cancel(message: Message, state: FSMContext):
    await message.answer(LEXICON_RU["commands"]["cancel"])
    await state.clear()