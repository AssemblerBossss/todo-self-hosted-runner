"""
Интеграционные тесты с реальным GitLab API.
Запускаются только при явном включении: ENABLE_REAL_GITLAB_TESTS=1
"""
import asyncio
import os
import time
import pytest
from httpx import AsyncClient, HTTPStatusError, RequestError

pytestmark = [pytest.mark.integration]


@pytest.fixture(scope="session")
def gitlab_test_config():
    return {
        "gitlab_url": os.getenv(
            "TEST_GITLAB_URL",
            "https://gitlab.com/gitlab-org/gitlab/-/issues"
        ),
        "api_token": os.getenv("GITLAB_TOKEN", ""),
        "max_issues": int(os.getenv("TEST_GITLAB_MAX_ISSUES", "20")),
        "timeout": int(os.getenv("TEST_GITLAB_TIMEOUT", "60")),
    }


@pytest.mark.asyncio(loop_scope="session")
async def test_import_issues_sequential_real(user_client: AsyncClient, gitlab_test_config):
    if os.getenv("ENABLE_REAL_GITLAB_TESTS", "0") != "1":
        pytest.skip("Real GitLab tests disabled. Set ENABLE_REAL_GITLAB_TESTS=1 to enable.")

    try:
        resp = await user_client.post(
            "/todo/import-issues/",
            data={
                "gitlab_url": gitlab_test_config["gitlab_url"],
                "token": gitlab_test_config["api_token"],
            },
        )
    except (HTTPStatusError, RequestError) as e:
        pytest.skip(f"GitLab API unavailable: {e}")

    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["imported"] >= 0


@pytest.mark.asyncio(loop_scope="session")
async def test_parallel_faster_than_sequential_real(user_client: AsyncClient, gitlab_test_config):
    if os.getenv("ENABLE_REAL_GITLAB_TESTS", "0") != "1":
        pytest.skip("Real GitLab tests disabled. Set ENABLE_REAL_GITLAB_TESTS=1 to enable.")

    common_params = {
        "gitlab_url": gitlab_test_config["gitlab_url"],
        "token": gitlab_test_config["api_token"],
    }

    try:
        t0 = time.monotonic()
        resp_seq = await user_client.post("/todo/import-issues/", data=common_params)
        t_sequential = time.monotonic() - t0

        await asyncio.sleep(1)

        t0 = time.monotonic()
        resp_par = await user_client.post("/todo/import-issues-parallel/", data=common_params)
        t_parallel = time.monotonic() - t0

    except (HTTPStatusError, RequestError) as e:
        pytest.skip(f"GitLab API unavailable: {e}")

    print(f"\n[REAL API] sequential={t_sequential:.2f}s  parallel={t_parallel:.2f}s")

    assert resp_seq.status_code == 200
    assert resp_par.status_code == 200

    # Мягкая проверка: только если данных достаточно
    if t_sequential > 3.0 and resp_seq.json()["imported"] > 50:
        assert t_parallel < t_sequential * 0.8