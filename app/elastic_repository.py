from elasticsearch import AsyncElasticsearch, NotFoundError
from typing import Optional
import logging

from app.models import Todo

logger = logging.getLogger(__name__)

INDEX_NAME = "todos"

TODOS_MAPPING = {
    "mappings": {
        "properties": {
            "todo_id":      {"type": "integer"},
            "title":        {"type": "text", "analyzer": "standard"},
            "details":      {"type": "text", "analyzer": "standard"},
            "tag":          {"type": "keyword"},
            "created_at":   {"type": "date"},
            "completed":    {"type": "boolean"},
            "completed_at": {"type": "date"},
        }
    }
}


class ElasticRepository:
    def __init__(self, client: AsyncElasticsearch):
        self._client = client

    async def ensure_index_exists(self):
        """Создает индекс с маппингом, если он еще не существует."""
        exists = await self._client.indices.exists(index=INDEX_NAME)
        if not exists:
            await self._client.indices.create(index=INDEX_NAME, body=TODOS_MAPPING)
            logger.info("Index '%s' created.", INDEX_NAME)

    async def index_todo(self, todo: Todo):
        """Добавляет или обновляет документ задачи."""
        try:
            await self._client.index(
                index=INDEX_NAME,
                id=str(todo.id),
                document={
                    "todo_id":      todo.id,
                    "title":        todo.title,
                    "details":      todo.details,
                    "tag":          todo.tag,
                    "created_at":   todo.created_at.isoformat() if todo.created_at else None,
                    "completed":    todo.completed,
                    "completed_at": todo.completed_at.isoformat() if todo.completed_at else None,
                }
            )
        except Exception as e:
            logger.error("Failed to index todo %s: %s", todo.id, e)

    async def update_todo(self,todo_id: int,  todo: Todo):
        """Частично обновляет документ задачи."""
        try:
            await self._client.update(
                index=INDEX_NAME,
                id=str(todo_id),
                doc={
                    "title":        todo.title,
                    "details":      todo.details,
                    "tag":          todo.tag,
                    "completed":    todo.completed,
                    "completed_at": todo.completed_at.isoformat() if todo.completed_at else None,
                }
            )
        except NotFoundError:
            logger.warning("Todo %s not found in index on update.", todo.id)
        except Exception as e:
            logger.error("Failed to update todo %s in index: %s", todo.id, e)

    async def delete_todo(self, todo_id: int):
        """Удаляет документ задачи из индекса."""
        try:
            await self._client.delete(index=INDEX_NAME, id=str(todo_id))
        except NotFoundError:
            logger.warning("Todo %s not found in index on delete.", todo_id)
        except Exception as e:
            logger.error("Failed to delete todo %s from index: %s", todo_id, e)

    async def search_todos(
            self,
            query_text: str,
            tag: Optional[str] = None,
            limit: int = 10,
            skip: int = 0
    ) -> list[dict]:
        """Полнотекстовый поиск по title и details."""
        must_clauses = [
            {
                "multi_match": {
                    "query":  query_text,
                    "fields": ["title", "details"],
                }
            }
        ]
        if tag:
            must_clauses.append({"term": {"tag": tag}})

        try:
            response = await self._client.search(
                index=INDEX_NAME,
                body={
                    "from":  skip,
                    "size":  limit,
                    "query": {"bool": {"must": must_clauses}},
                    "sort":  [{"created_at": {"order": "desc"}}],
                }
            )
            return [hit["_source"] for hit in response["hits"]["hits"]]
        except Exception as e:
            logger.error("Search failed: %s", e)
            return []