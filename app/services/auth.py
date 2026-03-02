from fastapi import Request

from app.core import UnitOfWork
from app.models import User
from app.exceptions import UserAlreadyExists, InvalidCredentials, InactiveUser


class AuthService:
    """Auth service"""

    async def register(self, *, username: str, password: str, uow_session: UnitOfWork):
        async with uow_session.start():
            existing_user = await uow_session.auth.get_user(username)
            if existing_user:
                raise UserAlreadyExists()

            user = User(username=username, password=password, disabled=False)

            await uow_session.auth.add_user(user)

    async def login(self, *, username: str, password: str, uow_session: UnitOfWork):
        async with uow_session.start():
            user = await uow_session.auth.get_user(username)
            if not user or user.password != password:
                raise InvalidCredentials()

            if user.disabled:
                raise InactiveUser()

            await uow_session.auth.set_disabled(username, False)

            return user

    async def logout(
        self,
        *,
        username: str,
        uow_session: UnitOfWork,
    ) -> None:

        async with uow_session.start():
            await uow_session.auth.set_disabled(username, True)
