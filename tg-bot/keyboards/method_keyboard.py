from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from lexicon import LEXICON_RU


gatys_button = InlineKeyboardButton(
    text=LEXICON_RU["buttons"]["gatys_button"],
    callback_data="gatys"
)

adain_button = InlineKeyboardButton(
    text=LEXICON_RU["buttons"]["adain_button"],
    callback_data="adain"
)


method_keyboard = InlineKeyboardMarkup(inline_keyboard=[[gatys_button], [adain_button]])