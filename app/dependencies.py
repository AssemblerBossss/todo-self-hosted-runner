from elasticsearch import AsyncElasticsearch
from app.services import AuthService


def get_auth_service() -> AuthService:
    # пока stateless — создаём каждый раз
    # позже можно внедрить config, logger и т.д.
    return AuthService()