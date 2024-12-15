from typing import Final

from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.methods import SendMessage
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message, ReplyKeyboardRemove

from config_data.config import config
from database.methods.user import change_user_base_currency, has_pro_plan
from handlers.menu import answer_with_menu, get_menu_keyboard, get_menu_text
from keyboards.keyboards_utils import create_currencies_keyboard
from states.states import MenuState, SettingsState, add_to_delete_pool, get_deleted_messages_pool, delete_message_pool

CALLBACK_CHANGE_CURRENCY: Final[str] = 'change_base_currency'


router = Router()


@router.callback_query(MenuState.idle, F.data == 'settings')
async def settings(callback: CallbackQuery, state: FSMContext):
    await answer_with_settings(callback.bot, callback.message.chat.id, callback.message.message_id, state)
    await add_to_delete_pool(state, callback.message.message_id)



@router.callback_query(SettingsState.pending_for_symbol, F.data == 'stop')
async def stop(callback: CallbackQuery, state: FSMContext):
    await delete_message_pool(callback.bot, callback.message.chat.id, state)
    await answer_with_menu(callback.bot, callback.message.chat.id, callback.message.message_id, state)


@router.callback_query(SettingsState.idle, F.data == CALLBACK_CHANGE_CURRENCY)
async def change_base_currency(callback: CallbackQuery, state: FSMContext):
    await callback.bot.edit_message_reply_markup(
        message_id=callback.message.message_id,
        chat_id=callback.message.chat.id,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='❌ Прекратить ввод', callback_data='stop')]
            ]
        )
    )
    new_message = await callback.message.answer(
        text='Выберите основную валюту для просмотра курса',
        reply_markup=create_currencies_keyboard(config.currencies)
    )
    await add_to_delete_pool(state, new_message.message_id)
    await state.set_state(SettingsState.pending_for_symbol)


@router.message(SettingsState.pending_for_symbol)
async def on_input_symbol(message: Message, state: FSMContext):
    if message.text in config.currencies:
        await state.set_state(SettingsState.idle)
        await change_user_base_currency(message.from_user.id, message.text)

        new_message = await message.bot.send_message(
            text='✅ Данные сохранены',
            chat_id=message.chat.id,
            reply_markup=ReplyKeyboardRemove()
        )
        await add_to_delete_pool(state, message.message_id)
        await add_to_delete_pool(state, new_message.message_id)

        has_plan = await has_pro_plan(message.chat.id)
        await delete_message_pool(message.bot, message.chat.id, state)
        await message.bot.send_message(
            chat_id=message.chat.id,
            text=get_menu_text(has_plan),
            reply_markup=get_menu_keyboard(has_plan)
        )
    else:
        new_message = await message.answer(
            text='❌ Такой валюты не существует, попробуйте снова',
            reply_markup=create_currencies_keyboard(config.currencies)
        )
        await add_to_delete_pool(state, new_message.message_id)


async def answer_with_settings(
        bot: Bot,
        chat_id: int,
        message_id: int,
        state: FSMContext
):
    await state.set_state(SettingsState.idle)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Поменять базовую валюту', callback_data=CALLBACK_CHANGE_CURRENCY)],
            [InlineKeyboardButton(text='⬅️ Назад', callback_data='menu')]
        ]
    )
    text = '⚙️ Настройки\n\nНастройте базовый курс валюты здесь'

    try:
        await bot.edit_message_text(
            text=text,
            message_id=message_id,
            chat_id=chat_id
        )
        await bot.edit_message_reply_markup(
            reply_markup=keyboard,
            message_id=message_id,
            chat_id=chat_id
        )
    except TelegramBadRequest:
        await bot.send_message(
            text=text,
            chat_id=chat_id,
            reply_markup=keyboard
        )
