# app/utils/gitlab_url.py
import re
from urllib.parse import urlparse, quote

def gitlab_url_to_api(web_url: str, api_base: str = "https://gitlab.com/api/v4") -> str:
    """
    Конвертирует GitLab URL в формат API v4.

    Поддерживает:
    - Веб-интерфейс: https://gitlab.com/group/project/-/issues
    - API v4: https://gitlab.com/api/v4/projects/:id/issues (возвращает как есть)
    - Project ID: 278964 (если передан как число)

    Returns:
        API endpoint: https://gitlab.com/api/v4/projects/:encoded_path_or_id/issues
    """
    # Если уже API URL — возвращаем как есть
    if "/api/v4/" in web_url:
        return web_url.rstrip("/")

    # Если передан просто ID проекта (число)
    if web_url.isdigit():
        return f"{api_base}/projects/{web_url}/issues"

    # Парсим веб-ссылку
    parsed = urlparse(web_url)
    path = parsed.path.rstrip("/")

    # Паттерн: /:namespace/:project/-/issues
    match = re.match(r"^/([^/]+/[^/]+)/-/issues/?$", path)
    if not match:
        # Паттерн для подгрупп: /:namespace/:subgroup/:project/-/issues
        match = re.match(r"^/(.+)/-/issues/?$", path)
        if not match:
            raise ValueError(
                f"Некорректный GitLab URL. Ожидается формат:\n"
                f"  https://gitlab.com/<namespace>/<project>/-/issues\n"
                f"  или API: https://gitlab.com/api/v4/projects/<id>/issues\n"
                f"  Получено: {web_url}"
            )

    project_path = match.group(1)  # e.g., "gitlab-org/gitlab" или "group/subgroup/project"

    # URL-encode для поддержки спецсимволов в пути
    encoded_path = quote(project_path, safe="")

    return f"{api_base}/projects/{encoded_path}/issues"