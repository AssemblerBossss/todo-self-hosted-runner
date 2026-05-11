# tests/integration/test_gitlab_import_real.py
import asyncio
import time
import os
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.integration  # маркер для пропуска в CI по умолчанию
async def test_import_issues_sequential_real(user_client: AsyncClient, gitlab_test_config):
    """Тест последовательного импорта на реальном проекте."""

    # Пропускаем, если нет доступа к сети (локальная разработка)
    if os.getenv("SKIP_INTEGRATION_TESTS"):
        pytest.skip("Integration tests disabled")

    resp = await user_client.post(
        "/todo/import-issues/",
        data={
            "gitlab_url": f"{gitlab_test_config['project_url']}/-/issues",
            "token": gitlab_test_config["api_token"],
            "limit": gitlab_test_config["max_issues"],  # ваш параметр для лимита
        },
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["imported"] > 0  # хотя бы что-то импортировалось
    assert data["imported"] <= gitlab_test_config["max_issues"]


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.integration
async def test_parallel_faster_than_sequential_real(user_client: AsyncClient, gitlab_test_config):
    """Сравнение производительности на реальных данных."""

    if os.getenv("SKIP_INTEGRATION_TESTS"):
        pytest.skip("Integration tests disabled")

    common_params = {
        "gitlab_url": f"{gitlab_test_config['project_url']}/-/issues",
        "token": gitlab_test_config["api_token"],
        "limit": 100,  # меньше страниц для быстрого теста
    }

    # Последовательный импорт
    t0 = time.monotonic()
    resp_seq = await user_client.post("/todo/import-issues/", data=common_params)
    t_sequential = time.monotonic() - t0

    # Небольшая пауза между запросами, чтобы не получить rate limit
    await asyncio.sleep(2)

    # Параллельный импорт
    t0 = time.monotonic()
    resp_par = await user_client.post("/todo/import-issues-parallel/", data=common_params)
    t_parallel = time.monotonic() - t0

    print(f"\n[REAL API] sequential={t_sequential:.2f}s  parallel={t_parallel:.2f}s")

    # Параллельный должен быть быстрее (с запасом на сетевые флуктуации)
    assert resp_seq.status_code == 200
    assert resp_par.status_code == 200
    assert t_parallel < t_sequential * 0.9  # 10% запас на погрешность