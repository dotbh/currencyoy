from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def create_currencies_keyboard(currencies: list[str]) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    row = []

    for cur in currencies:
        row.append(KeyboardButton(text=cur))

        if len(row) == 4:
            kb.add(*row)
            row = []

    if row:
        kb.add(*row)

    return kb.as_markup(resize_keyboard=True)


