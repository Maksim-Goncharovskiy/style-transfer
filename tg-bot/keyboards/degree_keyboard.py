from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


buttons = [InlineKeyboardButton(text=str(i), callback_data=str(i)) for i in range(1, 6)]

degree_keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])