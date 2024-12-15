from types import NoneType

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiohttp.web_routedef import delete

last_message: dict[int, int]

class ConvertState(StatesGroup):
    pending_from_currency = State()
    pending_to_currency = State()
    pending_currency_value = State()
    check_cur = State()


class MenuState(StatesGroup):
    idle = State()


class SettingsState(StatesGroup):
    idle = State()
    pending_for_symbol = State()


# Утилита для добавления сообщений для удаления после завершения действия в боте
async def get_deleted_messages_pool(state: FSMContext) -> list[int]:
    data = await state.get_data()
    if 'delete' not in data.keys():
        return []
    return data.get('delete')


async def add_to_delete_pool(state: FSMContext, message_id: int):
    try:
        deleted_messages = await get_deleted_messages_pool(state)
        deleted_messages.append(message_id)
    except KeyError:
        deleted_messages = [message_id]

    await state.update_data(delete=deleted_messages)


async def delete_message_pool(bot: Bot, chat_id: int, state: FSMContext):
    message_ids = await get_deleted_messages_pool(state)

    await bot.delete_messages(
        chat_id=chat_id,
        message_ids=message_ids,
    )
    await state.update_data(delete=[])