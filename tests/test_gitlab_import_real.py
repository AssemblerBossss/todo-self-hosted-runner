import asyncio
import os
import time
import pytest
from httpx import AsyncClient

pytestmark = [pytest.mark.integration]


@pytest.mark.asyncio(loop_scope="session")
async def test_import_issues_sequential_real(user_client: AsyncClient, gitlab_test_config):
    """Тест последовательного импорта на реальном проекте."""

    # Пропускаем, если интеграционные тесты отключены
    if os.getenv("SKIP_INTEGRATION_TESTS", "false").lower() == "true":
        pytest.skip("Integration tests disabled via SKIP_INTEGRATION_TESTS")

    # Пропускаем, если нет сетевого доступа (локальная разработка без сети)
    if os.getenv("CI") != "true" and not os.getenv("ENABLE_REAL_GITLAB_TESTS"):
        pytest.skip("Real GitLab tests disabled locally. Set ENABLE_REAL_GITLAB_TESTS=1 to enable.")

    resp = await user_client.post(
        "/todo/import-issues/",
        data={
            "gitlab_url": f"{gitlab_test_config['project_url']}/-/issues",
            "token": gitlab_test_config["api_token"],
            "limit": gitlab_test_config["max_issues"],
        },
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["imported"] > 0
    assert data["imported"] <= gitlab_test_config["max_issues"]


@pytest.mark.asyncio(loop_scope="session")
async def test_parallel_faster_than_sequential_real(user_client: AsyncClient, gitlab_test_config):
    """Сравнение производительности на реальных данных."""

    if os.getenv("SKIP_INTEGRATION_TESTS", "false").lower() == "true":
        pytest.skip("Integration tests disabled via SKIP_INTEGRATION_TESTS")

    if os.getenv("CI") != "true" and not os.getenv("ENABLE_REAL_GITLAB_TESTS"):
        pytest.skip("Real GitLab tests disabled locally.")

    common_params = {
        "gitlab_url": f"{gitlab_test_config['project_url']}/-/issues",
        "token": gitlab_test_config["api_token"],
        "limit": 100,  # меньше страниц для быстрого теста
    }

    # Последовательный импорт
    t0 = time.monotonic()
    resp_seq = await user_client.post("/todo/import-issues/", data=common_params)
    t_sequential = time.monotonic() - t0

    # Пауза между запросами, чтобы избежать rate limit
    await asyncio.sleep(2)

    # Параллельный импорт
    t0 = time.monotonic()
    resp_par = await user_client.post("/todo/import-issues-parallel/", data=common_params)
    t_parallel = time.monotonic() - t0

    print(f"\n[REAL API] sequential={t_sequential:.2f}s  parallel={t_parallel:.2f}s")

    assert resp_seq.status_code == 200
    assert resp_par.status_code == 200
    # Параллельный должен быть быстрее с запасом на сетевые флуктуации
    assert t_parallel < t_sequential * 0.95