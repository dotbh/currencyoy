from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from database.methods.user import register_user, has_pro_plan
from states.states import MenuState

router = Router()


@router.message(CommandStart())
async def on_start(message: Message, state: FSMContext):
    await register_user(user_id=message.from_user.id)
    await message.delete()
    await answer_with_menu(message.bot, message.chat.id, message.message_id, state)


@router.callback_query(F.data == 'menu')
async def menu(callback: CallbackQuery, state: FSMContext):
    await answer_with_menu(callback.bot, callback.message.chat.id, callback.message.message_id, state)



def get_menu_text(has_pro: bool) -> str:
    plan = '💿 Обычный план'
    if has_pro:
        plan = '📀 Профессиональный план'
    return f'📜 МЕНЮ\n\n{plan}\n💱 Для выбора просмотра курса выберите основную валюту в настройках\n'


def get_menu_keyboard(has_pro: bool) -> InlineKeyboardMarkup:
    pro_button: InlineKeyboardButton

    if has_pro:
        pro_button = InlineKeyboardButton(text='📈️ Смотреть курс', callback_data='view_currency')
    else:
        pro_button = InlineKeyboardButton(text='🗝️ Улучшить план (🔒 Смотреть курс)', callback_data='upgrade_plan')

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='🕗 История конвертаций', callback_data='history')],
            [InlineKeyboardButton(text='⚙️ Настройки', callback_data='settings')],
            [InlineKeyboardButton(text='💱 Конвертировать', callback_data='convert')],
            [pro_button]
        ]
    )
    return keyboard


async def answer_with_menu(
        bot: Bot,
        chat_id: int,
        message_id: int,
        state: FSMContext
):
    await state.set_state(MenuState.idle)
    has_pro = await has_pro_plan(chat_id)

    try:
        await bot.edit_message_text(
            text=get_menu_text(has_pro),
            message_id=message_id,
            chat_id=chat_id
        )
        await bot.edit_message_reply_markup(
            reply_markup=get_menu_keyboard(has_pro),
            message_id=message_id,
            chat_id=chat_id
        )
    except TelegramBadRequest:
        await bot.send_message(
            text=get_menu_text(has_pro),
            chat_id=chat_id,
            reply_markup=get_menu_keyboard(has_pro)
        )