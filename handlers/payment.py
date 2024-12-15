from uuid import uuid4

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, LabeledPrice, PreCheckoutQuery, Message, InlineKeyboardMarkup, \
    InlineKeyboardButton

from config_data.config import config
from database.methods.user import upgrade_plan
from handlers.menu import answer_with_menu
from states.states import add_to_delete_pool, delete_message_pool, MenuState

router = Router()

@router.callback_query(F.data == 'cancel')
async def cancel(callback: CallbackQuery, state: FSMContext):
    await delete_message_pool(callback.bot, callback.message.chat.id, state)
    await answer_with_menu(callback.bot, callback.message.chat.id, callback.message.message_id, state)


@router.callback_query(F.data == 'upgrade_plan')
async def payment(callback: CallbackQuery, state: FSMContext):
    await callback.bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text='💰 Оплата Pro версии\n\nPro версия даст неограниченный доступ к просмотру курса валют'
    )
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Отменить', callback_data='cancel')]])
    )

    await state.update_data({'user_id': callback.message.from_user.id})
    m = await callback.message.answer_invoice(
        title='Оплата Pro версии',
        description='Предоставит доступ к продвинутой версии API',
        payload=str(uuid4()),
        provider_token=config.payment.provider_token,
        currency=config.payment.payment_currency,
        prices=[
            LabeledPrice(label='Pro версия', amount=config.payment.pro_plan_price)
        ]
    )
    await add_to_delete_pool(state, m.message_id)
    await add_to_delete_pool(state, callback.message.message_id)


@router.pre_checkout_query()
async def process_pre_checkout_query(query: PreCheckoutQuery):
    await query.bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=True)


@router.message(F.successful_payment)
async def success_plan_upgrade(message: Message, state: FSMContext):
    await upgrade_plan(message.from_user.id)
    await delete_message_pool(message.bot, message.chat.id, state)
    await answer_with_menu(
        bot=message.bot,
        chat_id=message.chat.id,
        message_id=message.message_id,
        state=state
    )