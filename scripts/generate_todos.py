"""
Скрипт генерации случайных тудушек.
Вызывает POST /todo/add/ для создания 20 тудушек со случайными данными.

Запуск:
    python generate_todos.py                                # локально
    docker exec app python /code/scripts/generate_todos.py  # через Docker
"""

import random
import sys
import http.client
import urllib.parse
from urllib.parse import urlparse

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
ADD_PATH = "/todo/add/"
COUNT = 20

TITLES = [
    "Купить продукты", "Сделать домашнее задание", "Позвонить маме",
    "Почитать книгу", "Сходить в спортзал", "Приготовить ужин",
    "Написать отчёт", "Изучить Python", "Посмотреть лекцию",
    "Починить велосипед", "Убраться в комнате", "Оплатить счета",
    "Записаться к врачу", "Составить план на неделю", "Полить цветы",
    "Обновить резюме", "Ответить на письма", "Настроить Docker",
    "Сделать бэкап данных", "Пройти онлайн-курс", "Написать тесты",
    "Отрефакторить код", "Прочитать документацию", "Сходить на прогулку",
    "Проверить почту", "Сделать презентацию", "Изучить Elasticsearch",
    "Запустить миграции", "Обновить зависимости", "Написать README"
]

DETAILS = [
    "Не забыть сделать это сегодня",
    "Важная задача, требует внимания",
    "Запланировано на эту неделю",
    "Низкий приоритет, но нужно сделать",
    "Срочно, дедлайн скоро",
    "Обсудить с командой перед выполнением",
    "Требует дополнительных ресурсов",
    "Можно делегировать при необходимости",
    "",
    "",
]

TAGS = ["Учёба", "Личное", "Планы"]
SOURCES = ["Созданная"]


def generate_todo() -> dict:
    title = random.choice(TITLES)
    suffix = random.randint(1, 9999)
    return {
        "title": f"{title} #{suffix}",
        "details": random.choice(DETAILS),
        "tag": random.choice(TAGS),
        "source": random.choice(SOURCES),
    }


def main():
    parsed = urlparse(BASE_URL)
    host = parsed.hostname
    port = parsed.port or (443 if parsed.scheme == "https" else 80)

    print(f"Генерация {COUNT} тудушек на {BASE_URL}{ADD_PATH}...")
    success = 0
    failed = 0

    for i in range(1, COUNT + 1):
        todo = generate_todo()
        body = urllib.parse.urlencode(todo).encode("utf-8")
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": str(len(body)),
        }

        conn = None
        try:
            if parsed.scheme == "https":
                conn = http.client.HTTPSConnection(host, port, timeout=10)
            else:
                conn = http.client.HTTPConnection(host, port, timeout=10)

            conn.request("POST", ADD_PATH, body=body, headers=headers)
            response = conn.getresponse()
            response_body = response.read().decode("utf-8", errors="replace")

            if response.status == 201:
                print(f"  [{i:02d}] ✅ Создана: {todo['title']}")
                success += 1
            else:
                print(f"  [{i:02d}] ❌ Ошибка {response.status}: {todo['title']} — {response_body}")
                failed += 1

        except ConnectionRefusedError:
            print(f"  [{i:02d}] ❌ Нет соединения с {BASE_URL}")
            failed += 1
            break
        except TimeoutError:
            print(f"  [{i:02d}] ❌ Таймаут запроса для: {todo['title']}")
            failed += 1
        except OSError as e:
            print(f"  [{i:02d}] ❌ Ошибка сети: {e}")
            failed += 1
            break
        finally:
            if conn:
                conn.close()

    print(f"\nГотово: {success} создано, {failed} ошибок.")


if __name__ == "__main__":
    main()