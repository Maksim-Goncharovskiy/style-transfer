from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from lexicon import LEXICON_RU


basic_router = Router()


@basic_router.message(Command(commands=["start"]))
async def say_hello(message: Message):
    await message.answer(LEXICON_RU["commands"]["start"])


@basic_router.message(Command(commands=["help"]))
async def provide_help(message: Message):
    await message.answer(LEXICON_RU["commands"]["help"])