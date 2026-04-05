"""
Тест-сьют 4: Получение статистики по item id — GET /api/1/statistic/:id
Покрывает: позитивные, негативные, корнер-кейсы, функциональные и нефункциональные проверки.
"""

import time
import pytest
import requests
import allure
from test_task_2_1.tests.conftest import BASE_URL, HEADERS_JSON, get_unique_seller_id

# ─────────────────────────────────────────────
# Вспомогательная функция
# ─────────────────────────────────────────────

def create_item_and_get_id(base_url, headers, seller_id, name, price, statistics):
    """
    Создаёт объявление через POST /api/1/item и возвращает его UUID.
    Извлекает id из поля status: "Сохранено - <UUID>".
    """
    payload = {
        "sellerID": seller_id,
        "name": name,
        "price": price,
        "statistics": statistics,
    }
    resp = requests.post(f"{base_url}/api/1/item", json=payload, headers=headers)
    assert resp.status_code == 200, f"Не удалось создать объявление: {resp.text}"
    item_id = resp.json()["status"].split(" - ")[-1].strip()
    assert item_id, "Пустой id в ответе сервера"
    return item_id


# ─────────────────────────────────────────────
# Позитивные сценарии
# ─────────────────────────────────────────────

@allure.suite("Статистика объявления — GET /api/1/statistic/:id")
@allure.feature("Статистика")
@allure.story("Позитивные сценарии")
@allure.title("TC-4.1: Получение статистики по существующему id объявления")
@allure.severity(allure.severity_level.BLOCKER)
def test_get_statistic_existing_id(created_item):
    """TC-4.1: Получение статистики для существующего объявления должно вернуть 200 OK."""
    item_id = created_item["id"]

    with allure.step(f"Выполнить GET /api/1/statistic/{item_id}"):
        response = requests.get(
            f"{BASE_URL}/api/1/statistic/{item_id}",
            headers=HEADERS_JSON,
        )

    with allure.step("Проверить HTTP-статус 200 OK"):
        assert response.status_code == 200, (
            f"Ожидался статус 200, получен {response.status_code}. Тело: {response.text}"
        )

    data = response.json()

    with allure.step("Проверить, что ответ не пустой"):
        assert data, "Ответ пустой, ожидалась статистика"


@allure.suite("Статистика объявления — GET /api/1/statistic/:id")
@allure.feature("Статистика")
@allure.story("Позитивные сценарии")
@allure.title("TC-4.2: E2E — создать объявление со статистикой и проверить значения")
@allure.severity(allure.severity_level.CRITICAL)
def test_get_statistic_values_match_created(base_url, headers, unique_seller_id):
    """TC-4.2: E2E-тест: значения статистики в ответе должны совпадать с переданными при создании."""
    likes = 7
    view_count = 15
    contacts = 3

    with allure.step("Шаг 1: Создать объявление с конкретными значениями статистики"):
        item_id = create_item_and_get_id(
            base_url, headers, unique_seller_id,
            name="E2E статистика",
            price=100,
            statistics={"likes": likes, "viewCount": view_count, "contacts": contacts},
        )

    with allure.step(f"Шаг 2: Запросить статистику GET /api/1/statistic/{item_id}"):
        stat_resp = requests.get(
            f"{base_url}/api/1/statistic/{item_id}",
            headers=headers,
        )
        assert stat_resp.status_code == 200, (
            f"Ожидался статус 200, получен {stat_resp.status_code}. Тело: {stat_resp.text}"
        )

    data = stat_resp.json()
    stat = data[0] if isinstance(data, list) else data

    with allure.step(f"Шаг 3: Проверить значение likes = {likes}"):
        assert stat.get("likes") == likes, (
            f"likes: ожидалось {likes}, получено {stat.get('likes')}"
        )

    with allure.step(f"Шаг 4: Проверить значение viewCount = {view_count}"):
        assert stat.get("viewCount") == view_count, (
            f"viewCount: ожидалось {view_count}, получено {stat.get('viewCount')}"
        )

    with allure.step(f"Шаг 5: Проверить значение contacts = {contacts}"):
        assert stat.get("contacts") == contacts, (
            f"contacts: ожидалось {contacts}, получено {stat.get('contacts')}"
        )


@allure.suite("Статистика объявления — GET /api/1/statistic/:id")
@allure.feature("Статистика")
@allure.story("Функциональные проверки")
@allure.title("TC-4.3: Проверка структуры ответа статистики")
@allure.severity(allure.severity_level.CRITICAL)
def test_get_statistic_response_schema(created_item):
    """TC-4.3: Ответ GET /api/1/statistic/:id должен содержать все обязательные поля с корректными типами."""
    item_id = created_item["id"]  

    with allure.step(f"Выполнить GET /api/1/statistic/{item_id}"):
        response = requests.get(
            f"{BASE_URL}/api/1/statistic/{item_id}",
            headers=HEADERS_JSON,
        )

    assert response.status_code == 200
    data = response.json()

    with allure.step("Проверить, что ответ является массивом"):
        assert isinstance(data, list), f"Ответ должен быть массивом, получено: {type(data)}"

    stat = data[0] if data else {}

    with allure.step("Проверить наличие полей likes, viewCount, contacts"):
        for field in ("likes", "viewCount", "contacts"):
            assert field in stat, f"Поле '{field}' отсутствует в статистике"

    with allure.step("Проверить, что значения поля статистики — числа"):
        for field in ("likes", "viewCount", "contacts"):
            assert isinstance(stat[field], (int, float)), (
                f"Поле '{field}' должно быть числом, получено {type(stat[field])}"
            )

# ─────────────────────────────────────────────
# Негативные сценарии 
# ─────────────────────────────────────────────

@allure.suite("Статистика объявления — GET /api/1/statistic/:id")
@allure.feature("Статистика")
@allure.story("Негативные сценарии")
@allure.title("TC-4.4: Получение статистики по несуществующему id")
@allure.severity(allure.severity_level.CRITICAL)
def test_get_statistic_not_found():
    """TC-4.4: Запрос статистики по несуществующему id должен вернуть 404 Not Found."""
    non_existent_id = "00000000-0000-0000-0000-000000000000"

    with allure.step(f"Выполнить GET /api/1/statistic/{non_existent_id}"):
        response = requests.get(
            f"{BASE_URL}/api/1/statistic/{non_existent_id}",
            headers=HEADERS_JSON,
        )

    with allure.step("Проверить HTTP-статус 404 Not Found"):
        assert response.status_code == 404, (
            f"Ожидался статус 404, получен {response.status_code}. Тело: {response.text}"
        )


@allure.suite("Статистика объявления — GET /api/1/statistic/:id")
@allure.feature("Статистика")
@allure.story("Негативные сценарии")
@allure.title("TC-4.5: Получение статистики с невалидным форматом id (не UUID)")
@allure.severity(allure.severity_level.CRITICAL)
def test_get_statistic_invalid_id_format():
    """TC-4.5: Невалидный формат id должен возвращать 400 Bad Request."""
    with allure.step("Выполнить GET /api/1/statistic/invalid-id"):
        response = requests.get(
            f"{BASE_URL}/api/1/statistic/invalid-id",
            headers=HEADERS_JSON,
        )

    with allure.step("Проверить HTTP-статус 400 Bad Request"):
        assert response.status_code == 400, (
            f"Ожидался статус 400, получен {response.status_code}. Тело: {response.text}"
        )


@allure.suite("Статистика объявления — GET /api/1/statistic/:id")
@allure.feature("Статистика")
@allure.story("Негативные сценарии")
@allure.title("TC-4.6: Получение статистики с числом вместо UUID в id")
@allure.severity(allure.severity_level.CRITICAL)
def test_get_statistic_numeric_id():
    """TC-4.6: Числовое значение id должно вернуть 400 Bad Request."""
    with allure.step("Выполнить GET /api/1/statistic/12345"):
        response = requests.get(
            f"{BASE_URL}/api/1/statistic/12345",
            headers=HEADERS_JSON,
        )

    with allure.step("Проверить HTTP-статус 400 Bad Request"):
        assert response.status_code == 400, (
            f"Ожидался статус 400, получен {response.status_code}. Тело: {response.text}"
        )


# ─────────────────────────────────────────────
# Корнер-кейсы
# ─────────────────────────────────────────────

@allure.suite("Статистика объявления — GET /api/1/statistic/:id")
@allure.feature("Статистика")
@allure.story("Корнер-кейсы")
@allure.title("TC-4.7: Идемпотентность GET-запроса на статистику")
@allure.severity(allure.severity_level.NORMAL)
def test_get_statistic_idempotent(created_item):
    """TC-4.7: Повторный GET-запрос статистики по тому же id должен вернуть идентичный результат."""
    item_id = created_item["id"] 

    with allure.step("Выполнить первый GET-запрос статистики"):
        resp1 = requests.get(f"{BASE_URL}/api/1/statistic/{item_id}", headers=HEADERS_JSON)
    with allure.step("Выполнить второй GET-запрос статистики"):
        resp2 = requests.get(f"{BASE_URL}/api/1/statistic/{item_id}", headers=HEADERS_JSON)

    with allure.step("Проверить статусы 200"):
        assert resp1.status_code == 200
        assert resp2.status_code == 200

    with allure.step("Сравнить тела ответов — должны совпадать"):
        assert resp1.json() == resp2.json(), (
            "Ответы двух одинаковых GET-запросов статистики отличаются — нарушена идемпотентность"
        )


@allure.suite("Статистика объявления — GET /api/1/statistic/:id")
@allure.feature("Статистика")
@allure.story("Корнер-кейсы")
@allure.title("TC-4.8: Изоляция статистики — разные объявления имеют независимую статистику")
@allure.severity(allure.severity_level.CRITICAL)
def test_get_statistic_isolation(base_url, headers):
    """TC-4.8: Статистика объявления A не должна совпадать со статистикой объявления B."""
    seller_a = get_unique_seller_id()
    seller_b = get_unique_seller_id()

    with allure.step("Создать объявление A с likes=5"):
        id_a = create_item_and_get_id(
            base_url, headers, seller_a,
            name="Объявление A", price=100,
            statistics={"likes": 5, "viewCount": 10, "contacts": 1},
        )

    with allure.step("Создать объявление B с likes=10"):
        id_b = create_item_and_get_id(
            base_url, headers, seller_b,
            name="Объявление B", price=200,
            statistics={"likes": 10, "viewCount": 20, "contacts": 2},
        )

    with allure.step("Запросить статистику объявления A"):
        stat_a_resp = requests.get(f"{base_url}/api/1/statistic/{id_a}", headers=headers)
        assert stat_a_resp.status_code == 200
        stat_a = stat_a_resp.json()
        stat_a = stat_a[0] if isinstance(stat_a, list) else stat_a

    with allure.step("Запросить статистику объявления B"):
        stat_b_resp = requests.get(f"{base_url}/api/1/statistic/{id_b}", headers=headers)
        assert stat_b_resp.status_code == 200
        stat_b = stat_b_resp.json()
        stat_b = stat_b[0] if isinstance(stat_b, list) else stat_b

    with allure.step("Проверить, что likes объявления A = 5, а B = 10"):
        assert stat_a.get("likes") == 5, (
            f"Ожидалось likes=5 для объявления A, получено {stat_a.get('likes')}"
        )
        assert stat_b.get("likes") == 10, (
            f"Ожидалось likes=10 для объявления B, получено {stat_b.get('likes')}"
        )


# ─────────────────────────────────────────────
# Нефункциональные и функциональные проверки
# ─────────────────────────────────────────────


@allure.suite("Статистика объявления — GET /api/1/statistic/:id")
@allure.feature("Статистика")
@allure.story("Нефункциональные проверки")
@allure.title("TC-4.10: Проверка времени ответа при запросе статистики (< 2000 мс)")
@allure.severity(allure.severity_level.MINOR)
def test_get_statistic_response_time(created_item):
    """TC-4.9: Время ответа GET /api/1/statistic/:id не должно превышать 2000 мс."""
    item_id = created_item["id"]

    with allure.step("Замерить время выполнения GET-запроса статистики"):
        start = time.time()
        response = requests.get(
            f"{BASE_URL}/api/1/statistic/{item_id}",
            headers=HEADERS_JSON,
        )
        elapsed_ms = (time.time() - start) * 1000

    assert response.status_code == 200

    with allure.step(f"Проверить время ответа < 2000 мс (фактически: {elapsed_ms:.0f} мс)"):
        assert elapsed_ms < 2000, (
            f"Время ответа {elapsed_ms:.0f} мс превышает допустимые 2000 мс"
        )


@allure.suite("Статистика объявления — GET /api/1/statistic/:id")
@allure.feature("Статистика")
@allure.story("Нефункциональные проверки")
@allure.title("TC-4.11: Проверка заголовка Content-Type в ответе статистики")
@allure.severity(allure.severity_level.NORMAL)
def test_get_statistic_content_type_header(created_item):
    """TC-4.10: Ответ должен содержать заголовок Content-Type: application/json."""
    item_id = created_item["id"]  

    with allure.step(f"Выполнить GET /api/1/statistic/{item_id}"):
        response = requests.get(
            f"{BASE_URL}/api/1/statistic/{item_id}",
            headers=HEADERS_JSON,
        )

    assert response.status_code == 200

    with allure.step("Проверить заголовок Content-Type"):
        content_type = response.headers.get("Content-Type", "")
        assert "application/json" in content_type, (
            f"Ожидался Content-Type: application/json, получен: '{content_type}'"
        )
        
@allure.suite("Статистика объявления — GET /api/1/statistic/:id")
@allure.feature("Статистика")
@allure.story("Позитивные сценарии")
@allure.title("TC-4.11: Статистика с нулевыми значениями всех полей")
@allure.severity(allure.severity_level.NORMAL)
#@pytest.mark.xfail(
   # reason="BUG: API возвращает 400 при передаче нулевых значений статистики (ожидается 200)",
    #strict=True,
#)

def test_get_statistic_zero_values(base_url, headers, unique_seller_id):
    """TC-4.11: Нулевые значения статистики должны корректно сохраняться и возвращаться.
    
    """
    with allure.step ("Создать объявление с нулевой статистикой"):
        payload = {
            "sellerID": unique_seller_id,
            "name": "Нулевая статистика",
            "price": 100,
            "statistics": {"likes": 0, "viewCount": 0, "contacts": 0},
        }
        create_resp = requests.post(f"{base_url}/api/1/item", json=payload, headers=headers)
        assert create_resp.status_code == 200  
        item_id = create_resp.json()["status"].split(" - ")[-1].strip()

    with allure.step (f"Запросить статистику для объявления {item_id}"):
        stat_resp = requests.get(
            f"{base_url}/api/1/statistic/{item_id}",
            headers=headers,
        )
        assert stat_resp.status_code == 200

    data = stat_resp.json()
    stat = data[0] if isinstance(data, list) else data

    with allure.step ("Проверить, что все поля статистики равны 0"):
        assert stat.get("likes") == 0
        assert stat.get("viewCount") == 0
        assert stat.get("contacts") == 0