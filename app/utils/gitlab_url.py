import re
from urllib.parse import urlparse, quote

def gitlab_url_to_api(web_url: str, api_base: str = "https://gitlab.com/api/v4") -> str:
    """Конвертирует GitLab URL в API endpoint."""
    if "/api/v4/" in web_url:
        return web_url.rstrip("/")
    if web_url.isdigit():
        return f"{api_base}/projects/{web_url}/issues"

    parsed = urlparse(web_url)
    path = parsed.path.rstrip("/")

    # Паттерн: /:namespace/:project/-/issues
    match = re.match(r"^/([^/]+/[^/]+)/-/issues/?$", path)
    if not match:
        match = re.match(r"^/(.+)/-/issues/?$", path)
    if not match:
        # Fallback: берём последние две части пути как project path
        parts = [p for p in path.split("/") if p]
        if len(parts) >= 2:
            project_path = "/".join(parts[-2:])
        else:
            raise ValueError(f"Некорректный GitLab URL: {web_url}")
    else:
        project_path = match.group(1)

    encoded_path = quote(project_path, safe="")
    return f"{api_base}/projects/{encoded_path}/issues"