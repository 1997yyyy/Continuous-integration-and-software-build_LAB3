"""Генератор тестовой нагрузки: создаёт несколько трассировок в Jaeger.

Запуск (приложение должно быть уже поднято через docker compose):
    python scripts/load.py

Скрипт не требует внешних зависимостей — только стандартную библиотеку.
"""

import json
import sys
import time
import urllib.error
import urllib.request

BASE_URL = "http://localhost:8080"


def call(path: str) -> None:
    try:
        with urllib.request.urlopen(BASE_URL + path, timeout=5) as response:
            body = response.read().decode()
            print(f"{path:35} -> {response.status} {body[:80]}")
    except urllib.error.HTTPError as exc:
        print(f"{path:35} -> {exc.code} (ожидаемая ошибка)")
    except urllib.error.URLError as exc:
        sys.exit(f"Приложение недоступно по адресу {BASE_URL}: {exc.reason}")


def main() -> None:
    call("/health")
    call("/")
    for rolls in (1, 3, 5, 10):
        call(f"/rolldice?rolls={rolls}")
        time.sleep(0.2)
    call("/error")
    print(json.dumps({"status": "нагрузка сгенерирована"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
