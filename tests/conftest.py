import asyncio
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

from app.core.database import get_async_uow_session
from app.models.base import Base
from app.main import app
from app.core.uow import UnitOfWork
from app.config import get_db_url

engine_test = create_async_engine(get_db_url(), poolclass=NullPool)
async_session_maker = async_sessionmaker(engine_test, expire_on_commit=False)
uow = UnitOfWork(async_session_maker)
Base.metadata.bind = engine_test


async def override_get_async_uow_session() -> UnitOfWork:
    async with uow.start() as uow_session:
        yield uow_session


app.dependency_overrides[get_async_uow_session] = override_get_async_uow_session


def _make_mock_elastic_repo():
    mock_repo = MagicMock()
    mock_repo.ensure_index_exists = AsyncMock()
    mock_repo.index_document = AsyncMock()
    mock_repo.delete_todo = AsyncMock()
    mock_repo.delete_todos_by_ids = AsyncMock()
    mock_repo.search_todos = AsyncMock(return_value=[])
    mock_repo.search_by_tag = AsyncMock(return_value=[])
    mock_repo.search_by_date = AsyncMock(return_value=[])
    mock_repo.get_all_tags = AsyncMock(return_value=[])
    mock_repo.get_notes_per_day_by_user = AsyncMock(return_value=[])
    return mock_repo


@pytest.fixture(autouse=True, scope="session")
def mock_elastic():
    mock_repo = _make_mock_elastic_repo()
    with (
        patch.object(UnitOfWork, "elastic", new_callable=PropertyMock, return_value=mock_repo),
        patch("app.repository.elastic_repository.ElasticRepository.ensure_index_exists", new=AsyncMock()),
    ):
        yield


@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


class CustomEventLoopPolicy(asyncio.DefaultEventLoopPolicy):
    pass


@pytest.fixture(scope="session", autouse=True)
def event_loop_policy(request):
    return CustomEventLoopPolicy()


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
