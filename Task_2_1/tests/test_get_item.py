"""
Тест-сьют 2: Получение объявления по идентификатору — GET /api/1/item/:id
Покрывает: позитивные, негативные, корнер-кейсы, функциональные и нефункциональные проверки.
"""

import time
import pytest
import requests
import allure
from conftest import BASE_URL, HEADERS_JSON, get_unique_seller_id


# ─────────────────────────────────────────────
# Позитивные сценарии
# ─────────────────────────────────────────────

@allure.suite("Получение объявления по id — GET /api/1/item/:id")
@allure.feature("Получение объявления")
@allure.story("Позитивные сценарии")
@allure.title("TC-2.1: Получение объявления по существующему id")
@allure.severity(allure.severity_level.BLOCKER)
def test_get_item_by_existing_id(created_item):
    item_id = created_item["id"]

    with allure.step(f"Выполнить GET /api/1/item/{item_id}"):
        response = requests.get(
            f"{BASE_URL}/api/1/item/{item_id}",
            headers=HEADERS_JSON,
        )

    with allure.step("Проверить HTTP-статус 200 OK"):
        assert response.status_code == 200, (
            f"Ожидался статус 200, получен {response.status_code}. Тело: {response.text}"
        )

    data = response.json()

    with allure.step("Проверить, что ответ содержит данные (не пустой список)"):
        assert data, "Ответ пустой, ожидались данные объявления"


@allure.suite("Получение объявления по id — GET /api/1/item/:id")
@allure.feature("Получение объявления")
@allure.story("Позитивные сценарии")
@allure.title("TC-2.2: E2E — создать объявление и получить его, сравнить поля")
@allure.severity(allure.severity_level.CRITICAL)
def test_get_item_fields_match_created(base_url, headers, unique_seller_id):
    seller_id = unique_seller_id
    payload = {
        "sellerID": seller_id,
        "name": "E2E тест объявление",
        "price": 1500,
        "statistics": {
            "likes": 4,
            "viewCount": 8,
            "contacts": 2,
        },
    }

    with allure.step("Шаг 1: Создать объявление через POST /api/1/item"):
        create_resp = requests.post(
            f"{base_url}/api/1/item",
            json=payload,
            headers=headers,
        )
    assert create_resp.status_code == 200, (
        f"Не удалось создать объявление: {create_resp.status_code} {create_resp.text}"
    )
    created = create_resp.json()
    item_id = created["status"].split(" - ")[-1].strip()

    with allure.step(f"Шаг 2: Получить объявление через GET /api/1/item/{item_id}"):
        get_resp = requests.get(
            f"{base_url}/api/1/item/{item_id}",
            headers=headers,
        )
    assert get_resp.status_code == 200, (
        f"Ожидался статус 200, получен {get_resp.status_code}. Тело: {get_resp.text}"
    )

    data = get_resp.json()
    item = data[0] if isinstance(data, list) else data

    with allure.step("Шаг 3: Сравнить поле 'name'"):
        assert item.get("name") == payload["name"], (
            f"name: ожидалось '{payload['name']}', получено '{item.get('name')}'"
        )

    with allure.step("Шаг 4: Сравнить поле 'price'"):
        assert item.get("price") == payload["price"], (
            f"price: ожидалось {payload['price']}, получено {item.get('price')}"
        )

    with allure.step("Шаг 5: Сравнить поле 'sellerId'"):
        assert item.get("sellerId") == seller_id, (
            f"sellerId: ожидалось {seller_id}, получено {item.get('sellerId')}"
        )

    with allure.step("Шаг 6: Сравнить поля statistics"):
        stats = item.get("statistics", {})
        assert stats.get("likes") == payload["statistics"]["likes"]
        assert stats.get("viewCount") == payload["statistics"]["viewCount"]
        assert stats.get("contacts") == payload["statistics"]["contacts"]


@allure.suite("Получение объявления по id — GET /api/1/item/:id")
@allure.feature("Получение объявления")
@allure.story("Функциональные проверки")
@allure.title("TC-2.3: Проверка структуры ответа при получении объявления")
@allure.severity(allure.severity_level.CRITICAL)
def test_get_item_response_schema(created_item):
    """TC-2.3: Ответ GET /api/1/item/:id должен содержать все обязательные поля."""
    item_id = created_item["id"]

    with allure.step(f"Выполнить GET /api/1/item/{item_id}"):
        response = requests.get(
            f"{BASE_URL}/api/1/item/{item_id}",
            headers=HEADERS_JSON,
        )

    assert response.status_code == 200
    data = response.json()
    item = data[0] if isinstance(data, list) else data

    with allure.step("Проверить наличие обязательных полей в ответе"):
        for field in ("id", "sellerId", "name", "price", "statistics", "createdAt"):
            assert field in item, f"Поле '{field}' отсутствует в ответе"

    with allure.step("Проверить типы данных"):
        assert isinstance(item["id"], str), "Поле 'id' должно быть строкой"
        assert isinstance(item["price"], (int, float)), "Поле 'price' должно быть числом"
        assert isinstance(item["statistics"], dict), "Поле 'statistics' должно быть объектом"


# ─────────────────────────────────────────────
# Негативные сценарии
# ─────────────────────────────────────────────

@allure.suite("Получение объявления по id — GET /api/1/item/:id")
@allure.feature("Получение объявления")
@allure.story("Негативные сценарии")
@allure.title("TC-2.4: Получение объявления по несуществующему id (UUID нулей)")
@allure.severity(allure.severity_level.CRITICAL)
def test_get_item_not_found():
    """TC-2.4: Запрос по несуществующему id должен вернуть 404 Not Found."""
    non_existent_id = "00000000-0000-0000-0000-000000000000"

    with allure.step(f"Выполнить GET /api/1/item/{non_existent_id}"):
        response = requests.get(
            f"{BASE_URL}/api/1/item/{non_existent_id}",
            headers=HEADERS_JSON,
        )

    with allure.step("Проверить HTTP-статус 404 Not Found"):
        assert response.status_code == 404, (
            f"Ожидался статус 404, получен {response.status_code}. Тело: {response.text}"
        )


@allure.suite("Получение объявления по id — GET /api/1/item/:id")
@allure.feature("Получение объявления")
@allure.story("Негативные сценарии")
@allure.title("TC-2.5: Получение объявления с невалидным форматом id (не UUID)")
@allure.severity(allure.severity_level.CRITICAL)
def test_get_item_invalid_id_format():
    """TC-2.5: Невалидный формат id должен возвращать 400 Bad Request."""
    with allure.step("Выполнить GET /api/1/item/not-a-valid-uuid"):
        response = requests.get(
            f"{BASE_URL}/api/1/item/not-a-valid-uuid",
            headers=HEADERS_JSON,
        )

    with allure.step("Проверить HTTP-статус 400 Bad Request"):
        assert response.status_code == 400, (
            f"Ожидался статус 400, получен {response.status_code}. Тело: {response.text}"
        )


@allure.suite("Получение объявления по id — GET /api/1/item/:id")
@allure.feature("Получение объявления")
@allure.story("Негативные сценарии")
@allure.title("TC-2.6: Получение объявления с числом вместо UUID в id")
@allure.severity(allure.severity_level.CRITICAL)
def test_get_item_numeric_id():
    """TC-2.6: Числовое значение id должно вернуть 400 Bad Request."""
    with allure.step("Выполнить GET /api/1/item/12345"):
        response = requests.get(
            f"{BASE_URL}/api/1/item/12345",
            headers=HEADERS_JSON,
        )

    with allure.step("Проверить HTTP-статус 400 Bad Request"):
        assert response.status_code == 400, (
            f"Ожидался статус 400, получен {response.status_code}. Тело: {response.text}"
        )

allure.suite("Получение объявления по id — GET /api/1/item/:id")
@allure.feature("Получение объявления")
@allure.story("Корнер-кейсы")
@allure.title("TC-2.7: Получение объявления с пустым id (пробел в параметре пути)")
@allure.severity(allure.severity_level.NORMAL)
def test_get_item_empty_id():
    """
    TC-2.7: Запрос с пустым или состоящим из пробела id в пути URL.

    Проверяются два варианта пустого id:
      1. /api/1/item/%20  — id = пробел (URL-encoded)
      2. /api/1/item/     — пустой сегмент пути (trailing slash)

    Оба варианта не являются валидным UUID, поэтому API обязан вернуть
    400 Bad Request (невалидный формат id) или 404 Not Found
    (маршрут не найден — сервер не распознаёт путь без id-сегмента).
    Статус 200 недопустим: он означал бы, что API принял пустой id как корректный.
    """

    # ── Вариант 1: id = пробел (URL-encoded %20) ─────────────────────────────

    with allure.step("Вариант 1: выполнить GET /api/1/item/%20 (id = пробел, URL-encoded)"):
        response_space = requests.get(
            f"{BASE_URL}/api/1/item/%20",
            headers=HEADERS_JSON,
        )

    with allure.step(
        f"Проверить, что статус ответа — 400 Bad Request или 404 Not Found "
        f"(получен: {response_space.status_code})"
    ):
        assert response_space.status_code in (400, 404), (
            f"Ожидался статус 400 или 404 для id=пробел ('%20'), "
            f"получен {response_space.status_code}. Тело: {response_space.text}"
        )

    with allure.step("Проверить, что тело ответа непустое (содержит сообщение об ошибке)"):
        assert response_space.text.strip(), (
            "Тело ответа пустое — ожидалось информативное сообщение об ошибке"
        )


 # ── Вариант 2: пустой сегмент пути (trailing slash) ──────────────────────
    with allure.step("Вариант 2: выполнить GET /api/1/item/ (пустой сегмент — trailing slash)"):
        response_empty = requests.get(
            f"{BASE_URL}/api/1/item/",
            headers=HEADERS_JSON,
        )

    with allure.step(
        f"Проверить, что статус ответа — 400 Bad Request или 404 Not Found "
        f"(получен: {response_empty.status_code})"
    ):
        assert response_empty.status_code in (400, 404), (
            f"Ожидался статус 400 или 404 для пустого id (trailing slash), "
            f"получен {response_empty.status_code}. Тело: {response_empty.text}"
        )


# ─────────────────────────────────────────────
# Корнер-кейсы
# ─────────────────────────────────────────────

@allure.suite("Получение объявления по id — GET /api/1/item/:id")
@allure.feature("Получение объявления")
@allure.story("Корнер-кейсы")
@allure.title("TC-2.8: Идемпотентность GET-запроса по id")
@allure.severity(allure.severity_level.NORMAL)
def test_get_item_idempotent(created_item):
    """TC-2.8: Повторный GET-запрос по тому же id должен вернуть идентичный результат."""
    item_id = created_item["id"]

    with allure.step(f"Выполнить первый GET /api/1/item/{item_id}"):
        resp1 = requests.get(f"{BASE_URL}/api/1/item/{item_id}", headers=HEADERS_JSON)
    with allure.step(f"Выполнить второй GET /api/1/item/{item_id}"):
        resp2 = requests.get(f"{BASE_URL}/api/1/item/{item_id}", headers=HEADERS_JSON)

    with allure.step("Проверить, что оба ответа имеют статус 200"):
        assert resp1.status_code == 200
        assert resp2.status_code == 200

    with allure.step("Сравнить тела ответов — они должны совпадать"):
        assert resp1.json() == resp2.json(), (
            "Ответы двух одинаковых GET-запросов отличаются — нарушена идемпотентность"
        )


@allure.suite("Получение объявления по id — GET /api/1/item/:id")
@allure.feature("Получение объявления")
@allure.story("Корнер-кейсы")
@allure.title("TC-2.9: Получение объявления с id в верхнем регистре")
@allure.severity(allure.severity_level.MINOR)
def test_get_item_uppercase_uuid(created_item):
    """TC-2.9: Проверить, чувствителен ли API к регистру UUID в параметре id."""
    item_id_lower = created_item["id"]
    item_id_upper = item_id_lower.upper()

    with allure.step(f"Выполнить GET /api/1/item/{item_id_upper} (верхний регистр)"):
        response = requests.get(
            f"{BASE_URL}/api/1/item/{item_id_upper}",
            headers=HEADERS_JSON,
        )

    with allure.step("Проверить статус ответа — 200 или 404"):
        assert response.status_code in (200, 404), (
            f"Получен неожиданный статус: {response.status_code}. Тело: {response.text}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Нефункциональные и функциональные проверки
# ─────────────────────────────────────────────────────────────────────────────

@allure.suite("Получение объявления по id — GET /api/1/item/:id")
@allure.feature("Получение объявления")
@allure.story("Нефункциональные проверки")
@allure.title("TC-2.10: Проверка времени ответа при получении объявления по id (< 2000 мс)")
@allure.severity(allure.severity_level.MINOR)
def test_get_item_response_time(created_item):
    """TC-2.10: Время ответа на GET /api/1/item/:id не должно превышать 2000 мс."""
    item_id = created_item["id"]

    with allure.step("Замерить время выполнения GET-запроса"):
        start = time.time()
        response = requests.get(f"{BASE_URL}/api/1/item/{item_id}", headers=HEADERS_JSON)
        elapsed_ms = (time.time() - start) * 1000

    assert response.status_code == 200

    with allure.step(f"Проверить время ответа < 2000 мс (фактически: {elapsed_ms:.0f} мс)"):
        assert elapsed_ms < 2000, (
            f"Время ответа {elapsed_ms:.0f} мс превышает допустимые 2000 мс"
        )



@allure.suite("Получение объявления по id — GET /api/1/item/:id")
@allure.feature("Получение объявления")
@allure.story("Функциональные проверки")
@allure.title("TC-2.11: Проверка заголовка Content-Type в ответе")
@allure.severity(allure.severity_level.NORMAL)
def test_get_item_content_type_header(created_item):
    """TC-2.11: Ответ должен содержать заголовок Content-Type: application/json."""
    item_id = created_item["id"]

    with allure.step(f"Выполнить GET /api/1/item/{item_id}"):
        response = requests.get(f"{BASE_URL}/api/1/item/{item_id}", headers=HEADERS_JSON)

    assert response.status_code == 200

    with allure.step("Проверить заголовок Content-Type"):
        content_type = response.headers.get("Content-Type", "")
        assert "application/json" in content_type, (
            f"Ожидался Content-Type: application/json, получен: '{content_type}'"
        )
