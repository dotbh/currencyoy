from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton

from database.methods.history import get_user_history

router = Router()


@router.callback_query(F.data == 'history')
async def about(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='Назад',callback_data='menu')]]
    )
    history = await get_user_history(callback.message.chat.id)
    empty_text = ''
    if len(history) == 0:
        empty_text = '------ Пусто ------\n'

    await callback.bot.edit_message_text(
        text=f'🕗 История конвертаций\n\n{empty_text}{'\n'.join(history)}',
        message_id=callback.message.message_id,
        chat_id=callback.message.chat.id
    )
    await callback.bot.edit_message_reply_markup(
        reply_markup=keyboard,
        message_id=callback.message.message_id,
        chat_id=callback.message.chat.id
    )
