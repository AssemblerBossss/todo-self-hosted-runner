from sqlalchemy.ext.asyncio import AsyncSession

from app.repository import AuthRepository
from app.schemas import SUserRegister
from app.core import UnitOfWork
from app.models import User
from app.exceptions import UserAlreadyExists, InvalidCredentials, InactiveUser


class AuthService:
    """Auth service"""

    def __init__(self, session: AsyncSession):
        self.auth_repo = AuthRepository(session)

    async def register(self, *, username: str, password: str, uow_session: UnitOfWork):
        async with uow_session.start():
            existing_user = await uow_session.auth.get_user(username)
            if existing_user:
                raise UserAlreadyExists()

            user = User(username=username, password=password, disabled=False)

            await uow_session.auth.add_user(user)

    async def register_user(self, uow_session: UnitOfWork, user_data: SUserRegister) -> User:
        """Регистрирует нового пользователя."""
        async with uow_session.start():

            if await self.auth_repo.find_by_email(email=user_data.email):
                raise UserAlreadyExists()

            hashed_password = get_password_hash(user_data.password)

            user = User(
                email=user_data.email,
                hashed_password=hashed_password,
                role=user_data.role,
            )

            await self.user_repo.add(user)

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
