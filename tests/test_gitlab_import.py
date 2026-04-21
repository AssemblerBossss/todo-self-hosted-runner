"""
Тест запускается только при push в main (отдельный CI job test-gitlab-import).
Проверяет работоспособность обеих ручек и сравнивает время выполнения.
"""
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

@pytest.fixture(scope="module")
async def user_client(ac: AsyncClient) -> AsyncClient:
    await ac.post(
        "/auth/register",
        json={
            "email": "gitlab_user@example.com",
            "password": "password123",
            "confirm_password": "password123",
            "first_name": "Git",
            "last_name": "Lab",
        },
        follow_redirects=False,
    )
    await ac.post(
        "/auth/token",
        json={"email": "gitlab_user@example.com", "password": "password123"},
        follow_redirects=False,
    )
    return ac


MOCK_ISSUES = [{"title": f"Issue {i}", "description": f"desc {i}", "created_at": None} for i in range(2000)]
_PAGES = [MOCK_ISSUES[i : i + 100] for i in range(0, 2000, 100)]  # 20 страниц по 100


def _make_mock_response(page: int) -> MagicMock:
    mock = MagicMock()
    mock.raise_for_status = MagicMock()
    mock.json.return_value = _PAGES[page - 1] if 1 <= page <= len(_PAGES) else []
    mock.headers = {"x-total-pages": str(len(_PAGES))}
    return mock


@pytest.mark.asyncio(loop_scope="session")
async def test_import_issues_sequential_works(user_client: AsyncClient):
    """Последовательная ручка возвращает 200 и корректное число импортированных."""
    call_order = []

    async def fake_get(url, **kwargs):
        page = kwargs.get("params", {}).get("page", 1)
        call_order.append(page)
        await asyncio.sleep(0.02)
        return _make_mock_response(page)

    with (
        patch("httpx.AsyncClient.get", side_effect=fake_get),
        patch("app.services.todo.TodoService.create_from_gitlab_issues", new=AsyncMock()),
    ):
        resp = await user_client.post(
            "/todo/import-issues/",
            data={"gitlab_url": "http://fake-gitlab/issues", "token": "tok"},
        )

    assert resp.status_code == 200
    assert resp.json()["status"] == "success"
    assert resp.json()["imported"] == 2000
    assert call_order == sorted(call_order), "последовательная ручка должна обходить страницы по порядку"


@pytest.mark.asyncio(loop_scope="session")
async def test_import_issues_parallel_works(user_client: AsyncClient):
    """Параллельная ручка возвращает 200 и корректное число импортированных."""

    async def fake_get(url, **kwargs):
        page = kwargs.get("params", {}).get("page", 1)
        await asyncio.sleep(0.02)
        return _make_mock_response(page)

    with (
        patch("httpx.AsyncClient.get", side_effect=fake_get),
        patch("app.services.todo.TodoService.create_from_gitlab_issues", new=AsyncMock()),
    ):
        resp = await user_client.post(
            "/todo/import-issues-parallel/",
            data={"gitlab_url": "http://fake-gitlab/issues", "token": "tok"},
        )

    assert resp.status_code == 200
    assert resp.json()["status"] == "success"
    assert resp.json()["imported"] == 2000


@pytest.mark.asyncio(loop_scope="session")
async def test_parallel_import_faster_than_sequential(user_client: AsyncClient):
    """Параллельная ручка должна быть быстрее последовательной."""
    delay = 0.05  # имитация сетевой задержки на страницу

    async def fake_get_seq(url, **kwargs):
        page = kwargs.get("params", {}).get("page", 1)
        await asyncio.sleep(delay)
        return _make_mock_response(page)

    async def fake_get_par(url, **kwargs):
        page = kwargs.get("params", {}).get("page", 1)
        await asyncio.sleep(delay)
        return _make_mock_response(page)

    with (
        patch("app.services.todo.TodoService.create_from_gitlab_issues", new=AsyncMock()),
        patch("httpx.AsyncClient.get", side_effect=fake_get_seq),
    ):
        t0 = time.monotonic()
        await user_client.post(
            "/todo/import-issues/",
            data={"gitlab_url": "http://fake", "token": "tok"},
        )
        t_sequential = time.monotonic() - t0

    with (
        patch("app.services.todo.TodoService.create_from_gitlab_issues", new=AsyncMock()),
        patch("httpx.AsyncClient.get", side_effect=fake_get_par),
    ):
        t0 = time.monotonic()
        await user_client.post(
            "/todo/import-issues-parallel/",
            data={"gitlab_url": "http://fake", "token": "tok"},
        )
        t_parallel = time.monotonic() - t0

    print(f"\nsequential={t_sequential:.3f}s  parallel={t_parallel:.3f}s")
    assert t_parallel < t_sequential, (
        f"Параллельная ручка ({t_parallel:.3f}s) должна быть быстрее "
        f"последовательной ({t_sequential:.3f}s)"
    )