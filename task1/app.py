"""Лабораторная работа №3, задание 1.

Простое Flask-приложение (на основе официального примера OpenTelemetry
"Getting Started by Example") с ручной и автоматической инструментацией
трассировки.
"""

import logging
import random

from flask import Flask, jsonify, request
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

app = Flask(__name__)
logger = logging.getLogger(__name__)

tracer = trace.get_tracer(__name__)


@app.route("/")
def index():
    """Корневая страница со ссылками на демонстрационные эндпоинты."""
    return jsonify(
        service="lab3-task1-dice",
        endpoints={
            "/rolldice": "бросить кубик (параметр rolls=N)",
            "/error": "сгенерировать ошибку для проверки статуса спана",
            "/health": "проверка работоспособности",
        },
    )


@app.route("/rolldice")
def roll_dice():
    """Бросок кубика. Каждый бросок оформляется отдельным дочерним спаном."""
    rolls = request.args.get("rolls", default=1, type=int)
    rolls = max(1, min(rolls, 10))

    with tracer.start_as_current_span("roll-dice") as span:
        span.set_attribute("dice.rolls", rolls)

        results = [roll(i) for i in range(rolls)]

        span.add_event("dice.rolled", {"dice.results": str(results)})
        logger.info("Брошено кубиков: %s, результат: %s", rolls, results)

        return jsonify(results=results, total=sum(results))


def roll(index: int) -> int:
    """Один бросок кубика — отдельный спан, вложенный в roll-dice."""
    with tracer.start_as_current_span("roll") as span:
        value = random.randint(1, 6)
        span.set_attribute("dice.index", index)
        span.set_attribute("dice.value", value)
        return value


@app.route("/error")
def error():
    """Демонстрация ошибочного спана: статус ERROR и запись исключения."""
    with tracer.start_as_current_span("failing-operation") as span:
        try:
            raise RuntimeError("демонстрационная ошибка для Jaeger")
        except RuntimeError as exc:
            span.record_exception(exc)
            span.set_status(Status(StatusCode.ERROR, str(exc)))
            logger.exception("Ошибка в /error")
            return jsonify(error=str(exc)), 500


@app.route("/health")
def health():
    return jsonify(status="ok")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
