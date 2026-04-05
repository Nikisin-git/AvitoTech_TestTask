"""
Тест-сьют 3: Получение всех объявлений по идентификатору продавца — GET /api/1/:sellerId/item
"""

import time
import pytest
import requests
import allure
from conftest import BASE_URL, HEADERS_JSON, get_unique_seller_id


# ── Вспомогательная функция ──────────────────────────────────────────────────

def _create_item_get_id(base_url, headers, payload) -> str:
    """POST /api/1/item и вернуть UUID из поля status."""
    resp = requests.post(f"{base_url}/api/1/item", json=payload, headers=headers)
    assert resp.status_code == 200, (
        f"Не удалось создать объявление: {resp.status_code} {resp.text}"
    )
    # Ответ: {"status": "Сохранено - <UUID>"} — поля "id" нет!
    return resp.json()["status"].split(" - ")[-1].strip()


def _base_payload(seller_id: int, name: str, price: int) -> dict:
    """Возвращает минимально валидный payload для POST /api/1/item."""
    return {
        "sellerID": seller_id,
        "name": name,
        "price": price,
        "statistics": {             
            "likes": 1,             
            "viewCount": 1,
            "contacts": 1,
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# Позитивные сценарии
# ─────────────────────────────────────────────────────────────────────────────

@allure.suite("Объявления продавца — GET /api/1/:sellerId/item")
@allure.feature("Объявления продавца")
@allure.story("Позитивные сценарии")
@allure.title("TC-3.1: Получение объявлений по существующему sellerId")
@allure.severity(allure.severity_level.BLOCKER)
def test_get_items_by_seller_id_existing(base_url, headers, unique_seller_id):
    seller_id = unique_seller_id

    with allure.step(f"Создать объявление для продавца {seller_id}"):
        _create_item_get_id(base_url, headers, _base_payload(seller_id, "Объявление TC-3.1", 300))

    with allure.step(f"Выполнить GET /api/1/{seller_id}/item"):
        response = requests.get(f"{base_url}/api/1/{seller_id}/item", headers=headers)

    with allure.step("Проверить HTTP-статус 200 OK"):
        assert response.status_code == 200

    data = response.json()

    with allure.step("Проверить, что ответ является непустым массивом"):
        assert isinstance(data, list) and len(data) > 0

    with allure.step("Проверить, что все объявления принадлежат заданному продавцу"):
        for item in data:
            assert item.get("sellerId") == seller_id


@allure.suite("Объявления продавца — GET /api/1/:sellerId/item")
@allure.feature("Объявления продавца")
@allure.story("Позитивные сценарии")
@allure.title("TC-3.2: E2E — создать объявление и найти его в списке продавца")
@allure.severity(allure.severity_level.CRITICAL)
def test_get_seller_items_contains_created(base_url, headers, unique_seller_id):
    seller_id = unique_seller_id

    with allure.step(f"Шаг 1: Создать объявление для продавца {seller_id}"):
        created_id = _create_item_get_id(
            base_url, headers,
            _base_payload(seller_id, "E2E объявление продавца", 900)
        )

    with allure.step(f"Шаг 2: Получить список объявлений продавца {seller_id}"):
        list_resp = requests.get(f"{base_url}/api/1/{seller_id}/item", headers=headers)
        assert list_resp.status_code == 200

    item_ids = [item.get("id") for item in list_resp.json()]

    with allure.step(f"Шаг 3: Убедиться, что {created_id} присутствует в списке"):
        assert created_id in item_ids


@allure.suite("Объявления продавца — GET /api/1/:sellerId/item")
@allure.feature("Объявления продавца")
@allure.story("Позитивные сценарии")
@allure.title("TC-3.3: Получение нескольких объявлений одного продавца")
@allure.severity(allure.severity_level.CRITICAL)
def test_get_seller_items_multiple(base_url, headers, unique_seller_id):
    seller_id = unique_seller_id
    created_ids = []

    with allure.step(f"Создать 3 объявления для продавца {seller_id}"):
        for i in range(3):
            created_ids.append(_create_item_get_id(
                base_url, headers,
                _base_payload(seller_id, f"Объявление #{i + 1}", (i + 1) * 100)
            ))

    with allure.step(f"Получить список объявлений продавца {seller_id}"):
        list_resp = requests.get(f"{base_url}/api/1/{seller_id}/item", headers=headers)
        assert list_resp.status_code == 200

    returned_ids = [item.get("id") for item in list_resp.json()]

    with allure.step("Проверить, что все 3 объявления присутствуют"):
        for item_id in created_ids:
            assert item_id in returned_ids


@allure.suite("Объявления продавца — GET /api/1/:sellerId/item")
@allure.feature("Объявления продавца")
@allure.story("Позитивные сценарии")
@allure.title("TC-3.4: Продавец без объявлений")
@allure.severity(allure.severity_level.NORMAL)
def test_get_seller_items_empty_seller():
    seller_id = 111112
    with allure.step(f"GET /api/1/{seller_id}/item"):
        response = requests.get(f"{BASE_URL}/api/1/{seller_id}/item", headers=HEADERS_JSON)
    with allure.step("Статус 200 [] или 404"):
        assert response.status_code in (200, 404)
        if response.status_code == 200:
            assert isinstance(response.json(), list)


# ─────────────────────────────────────────────────────────────────────────────
# Негативные сценарии
# ─────────────────────────────────────────────────────────────────────────────

@allure.suite("Объявления продавца — GET /api/1/:sellerId/item")
@allure.feature("Объявления продавца")
@allure.story("Негативные сценарии")
@allure.title("TC-3.5: sellerId = строка")
@allure.severity(allure.severity_level.CRITICAL)
def test_get_seller_items_string_seller_id():
    with allure.step("GET /api/1/abcdef/item"):
        response = requests.get(f"{BASE_URL}/api/1/abcdef/item", headers=HEADERS_JSON)
    with allure.step("400 Bad Request"):
        assert response.status_code == 400


@allure.suite("Объявления продавца — GET /api/1/:sellerId/item")
@allure.feature("Объявления продавца")
@allure.story("Негативные сценарии")
@allure.title("TC-3.6: sellerId отрицательный")
@allure.severity(allure.severity_level.CRITICAL)
#@pytest.mark.xfail(strict=True, reason="BUG SERVER: -123456 принимается, возвращает 200 вместо 400")
def test_get_seller_items_negative_seller_id():
    with allure.step("GET /api/1/-123456/item"):
        response = requests.get(f"{BASE_URL}/api/1/-123456/item", headers=HEADERS_JSON)
    with allure.step("400 Bad Request"):
        assert response.status_code == 400


@allure.suite("Объявления продавца — GET /api/1/:sellerId/item")
@allure.feature("Объявления продавца")
@allure.story("Негативные сценарии")
@allure.title("TC-3.7: sellerId = 0")
@allure.severity(allure.severity_level.CRITICAL)
#@pytest.mark.xfail(strict=True, reason="BUG SERVER: 0 принимается, возвращает 200 [] вместо 400/404")
def test_get_seller_items_zero_seller_id():
    with allure.step("GET /api/1/0/item"):
        response = requests.get(f"{BASE_URL}/api/1/0/item", headers=HEADERS_JSON)
    with allure.step("400 или 404"):
        assert response.status_code in (400, 404)


@allure.suite("Объявления продавца — GET /api/1/:sellerId/item")
@allure.feature("Объявления продавца")
@allure.story("Негативные сценарии")
@allure.title("TC-3.8: sellerId очень большой")
@allure.severity(allure.severity_level.NORMAL)
#pytest.mark.xfail(strict=True, reason="BUG SERVER: 9999999999 принимается, возвращает 200 вместо 400/404")
def test_get_seller_items_very_large_seller_id():
    with allure.step("GET /api/1/9999999999/item"):
        response = requests.get(f"{BASE_URL}/api/1/9999999999/item", headers=HEADERS_JSON)
    with allure.step("400 или 404"):
        assert response.status_code in (400, 404)


# ─────────────────────────────────────────────────────────────────────────────
# Корнер-кейсы
# ─────────────────────────────────────────────────────────────────────────────

@allure.suite("Объявления продавца — GET /api/1/:sellerId/item")
@allure.feature("Объявления продавца")
@allure.story("Корнер-кейсы")
@allure.title("TC-3.9: Идемпотентность GET по sellerId")
@allure.severity(allure.severity_level.NORMAL)
def test_get_seller_items_idempotent(base_url, headers, unique_seller_id):
    seller_id = unique_seller_id

    with allure.step(f"Создать объявление для продавца {seller_id}"):
        _create_item_get_id(base_url, headers, _base_payload(seller_id, "Тест идемпотентности", 100))

    with allure.step("Первый GET"):
        resp1 = requests.get(f"{base_url}/api/1/{seller_id}/item", headers=headers)
    with allure.step("Второй GET"):
        resp2 = requests.get(f"{base_url}/api/1/{seller_id}/item", headers=headers)

    assert resp1.status_code == 200 and resp2.status_code == 200
    assert resp1.json() == resp2.json()


@allure.suite("Объявления продавца — GET /api/1/:sellerId/item")
@allure.feature("Объявления продавца")
@allure.story("Корнер-кейсы")
@allure.title("TC-3.10: Изоляция данных — объявления разных продавцов не пересекаются")
@allure.severity(allure.severity_level.CRITICAL)
def test_get_seller_items_data_isolation(base_url, headers):
    seller_a = get_unique_seller_id()
    seller_b = get_unique_seller_id()

    with allure.step(f"Создать объявление продавца A ({seller_a})"):
        id_a = _create_item_get_id(base_url, headers,
                                   _base_payload(seller_a, "Объявление A", 100))

    with allure.step(f"Создать объявление продавца B ({seller_b})"):
        id_b = _create_item_get_id(base_url, headers,
                                   _base_payload(seller_b, "Объявление B", 200))

    with allure.step("Объявления A нет в списке B и наоборот"):
        ids_a = [i.get("id") for i in
                 requests.get(f"{base_url}/api/1/{seller_a}/item", headers=headers).json()]
        ids_b = [i.get("id") for i in
                 requests.get(f"{base_url}/api/1/{seller_b}/item", headers=headers).json()]
        assert id_b not in ids_a
        assert id_a not in ids_b


# ─────────────────────────────────────────────────────────────────────────────
# Нефункциональные и функциональные проверки
# ─────────────────────────────────────────────────────────────────────────────

@allure.suite("Объявления продавца — GET /api/1/:sellerId/item")
@allure.feature("Объявления продавца")
@allure.story("Нефункциональные проверки")
@allure.title("TC-3.11: Время ответа < 2000 мс")
@allure.severity(allure.severity_level.MINOR)
def test_get_seller_items_response_time(base_url, headers, unique_seller_id):
    seller_id = unique_seller_id

    with allure.step("Создать объявление"):
        _create_item_get_id(base_url, headers,
                            _base_payload(seller_id, "Проверка производительности", 1))

    with allure.step("Замерить GET"):
        start = time.time()
        response = requests.get(f"{base_url}/api/1/{seller_id}/item", headers=headers)
        elapsed_ms = (time.time() - start) * 1000

    assert response.status_code == 200
    assert elapsed_ms < 2000, f"Время {elapsed_ms:.0f} мс > 2000 мс"


@allure.suite("Объявления продавца — GET /api/1/:sellerId/item")
@allure.feature("Объявления продавца")
@allure.story("Функциональные проверки")
@allure.title("TC-3.12: Структура элементов ответа")
@allure.severity(allure.severity_level.CRITICAL)
def test_get_seller_items_schema(base_url, headers, unique_seller_id):
    seller_id = unique_seller_id

    with allure.step("Создать объявление"):
        _create_item_get_id(base_url, headers, {
            "sellerID": seller_id,
            "name": "Проверка схемы",
            "price": 200,
            "statistics": {"likes": 1, "viewCount": 2, "contacts": 1},
        })

    with allure.step("GET список"):
        response = requests.get(f"{base_url}/api/1/{seller_id}/item", headers=headers)
        assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list) and len(data) > 0

    with allure.step("Проверить структуру каждого элемента"):
        for item in data:
            for field in ("id", "sellerId", "name", "price", "statistics", "createdAt"):
                assert field in item, f"Поле '{field}' отсутствует"