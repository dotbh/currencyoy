from typing import Annotated

from sqlalchemy.orm import Mapped, mapped_column

from database.database import Base

class User(Base):
    __tablename__ = 'users'

    user_id: Mapped[Annotated[int, mapped_column(primary_key=True)]]
    base_currency: Mapped[str] = mapped_column(default='RUB')
    pro_plan: Mapped[bool] = mapped_column(default=False)
    history: Mapped[str]
