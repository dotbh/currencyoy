from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, \
    ReplyKeyboardRemove

from config_data.config import config
from database.methods.history import add_history
from external_services.currencyapi import convert_currency
from handlers.menu import answer_with_menu
from keyboards.keyboards_utils import create_currencies_keyboard
from states.states import ConvertState, delete_message_pool, add_to_delete_pool

router = Router()


@router.callback_query(F.data == 'stop_converter')
async def stop(callback: CallbackQuery, state: FSMContext):
    await delete_message_pool(callback.bot, callback.message.chat.id, state)
    await answer_with_menu(callback.bot, callback.message.chat.id, callback.message.message_id, state)


@router.callback_query(F.data == 'convert')
async def select_from_cur(callback: CallbackQuery, state: FSMContext):
    cur_keyboard = create_currencies_keyboard(config.currencies)
    await state.set_state(ConvertState.pending_from_currency)
    await callback.bot.edit_message_text(
        text='💱 Конвертация валюты',
        message_id=callback.message.message_id,
        chat_id=callback.message.chat.id
    )
    await callback.bot.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='Прекратить', callback_data='stop_converter')]
            ]
        ),
        message_id=callback.message.message_id,
        chat_id=callback.message.chat.id
    )
    m = await callback.message.answer(
        text='Выберите какую валюту хотите перевести:',
        reply_markup=cur_keyboard
    )
    await add_to_delete_pool(state, m.message_id)
    await add_to_delete_pool(state, callback.message.message_id)


@router.message(ConvertState.pending_from_currency)
async def on_from_currency_input(message: Message, state: FSMContext):
    await add_to_delete_pool(state, message.message_id)
    if message.text not in config.currencies:
        m = await message.answer(
            text='Введенное значение не является валютой. Попробуй еще раз',
            reply_markup=create_currencies_keyboard(config.currencies)
        )
        await add_to_delete_pool(state, m.message_id)
        return
    await state.set_state(ConvertState.pending_currency_value)
    await state.update_data({'from': message.text})
    m = await message.answer(text='Введите количество выбранной валюты:', reply_markup=ReplyKeyboardRemove())
    await add_to_delete_pool(state, m.message_id)


@router.message(ConvertState.pending_currency_value, F.text)
async def on_currency_value_input(message: Message, state: FSMContext):
    await add_to_delete_pool(state, message.message_id)
    if not isint(message.text):
        m = await message.answer('Это не число')
        await add_to_delete_pool(state, m.message_id)
        return

    data = await state.get_data()
    await state.set_state(ConvertState.pending_to_currency)
    await state.update_data({'amount': int(message.text)})
    # Копируем список существующих валют и убераем уже выбранную валюту
    currencies = config.currencies.copy()
    currencies.remove(data['from'])
    cur_keyboard = create_currencies_keyboard(currencies)
    m = await message.answer('Теперь выберите в какую валюту хотите перевести:', reply_markup=cur_keyboard)
    await add_to_delete_pool(state, m.message_id)


@router.message(ConvertState.pending_to_currency)
async def on_to_currency_input(message: Message, state: FSMContext):
    await add_to_delete_pool(state, message.message_id)
    data = await state.get_data()
    from_cur: str = data['from']
    to_cur = message.text
    if to_cur not in config.currencies:
        currencies = config.currencies.copy()
        currencies.remove(from_cur)
        cur_keyboard = create_currencies_keyboard(currencies)
        m = await message.answer(text='❌ Введеное значение не является валютой. Попробуй заново', reply_markup=cur_keyboard)
        await add_to_delete_pool(state, m.message_id)
        return

    amount: int = data['amount']

    result = await convert_currency(base=from_cur, to=to_cur, amount=amount)
    text_result = f'{amount} {from_cur} = {result} {to_cur}'
    await delete_message_pool(message.bot, message.chat.id, state)
    await add_history(message.chat.id, text_result)
    await message.answer(
        text=f'🪙 Результат конвертации\n\n{text_result}',
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='OK', callback_data='menu')]]
        )
    )


def isint(s: str) -> bool:
    try:
        int(s)
        return True
    except ValueError:
        return False