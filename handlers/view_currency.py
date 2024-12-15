from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from config_data.config import config
from database.methods.user import get_user_base_currency
from external_services.currencyapi import get_currency_rates
from handlers.menu import answer_with_menu

router = Router()


@router.callback_query(F.data == 'view_currency')
async def view_currency(callback: CallbackQuery):
    user_base_currency: str = await get_user_base_currency(callback.from_user.id)

    currencies = config.currencies.copy()
    currencies.remove(user_base_currency)

    m = await callback.message.answer(
        text='♻️ Загрузка данных... (Не больше 10 секунд)'
    )
    rates: dict[str, float] = await get_currency_rates(base=user_base_currency, symbols=currencies)
    await m.delete()

    formatted_string = f'📈 Стоимость валюты к {user_base_currency}:\n'

    for symbol in rates.keys():
        value = rates[symbol]
        formatted_string += f'\n{symbol} = {value} {user_base_currency}'

    await callback.bot.edit_message_text(
        text=formatted_string,
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id
    )
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='⬅️ Назад', callback_data='menu')]]
        )
    )
