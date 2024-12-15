from database.database import session_factory
from database.models import User

# Имеет лимит хранилища в 15 историй
async def add_history(user_id: int, label: str):
    async with session_factory() as s:
        user = await s.get(User, user_id)

        history: list[str] = user.history.split(sep=',')
        if len(history[0]) == 0:
            del history[0]
        if len(history) == 15:
            del history[-1]
        history.append(label)

        user.history = ','.join(history)
        await s.commit()



async def get_user_history(user_id: int) -> list[str]:
    async with session_factory() as s:
        user = await s.get(User, user_id)
        history = user.history.split(sep=',')
        if len(history[0]) == 0:
            return []
        else:
            return history