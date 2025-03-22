from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from lexicon import LEXICON_RU


start_button = InlineKeyboardButton(
    text=LEXICON_RU["buttons"]["start_button"],
    callback_data="start_nst"
)

start_keyboard = InlineKeyboardMarkup(inline_keyboard=[[start_button]])