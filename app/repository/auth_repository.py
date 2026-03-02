from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from sqlalchemy import update
from app.models import User

class AuthRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_user(self, username: str) -> User:
        find_user = await self._session.execute(
            select(User).where(User.name == username)
        )
        data = find_user.scalars().one_or_none()
        return data

    async def set_disabled(self, username: str, value: bool):
        await self._session.execute(
            update(User).where(User.name == username).values(disabled=value)
        )

    async def add_user(self, user: User):
        self._session.add(user)
        await self._session.commit()
