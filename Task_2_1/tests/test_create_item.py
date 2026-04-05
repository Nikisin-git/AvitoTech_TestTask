"""
Тест-сьют 1: Создание объявления — POST /api/1/item

"""

import time
import uuid
import pytest
import requests
import allure
from test_task_2_1.tests.conftest import BASE_URL, HEADERS_JSON, get_unique_seller_id


# ─────────────────────────────────────────────
# Вспомогательные функции
# ─────────────────────────────────────────────

def _extract_id(response) -> str:
    """
    Извлечь UUID объявления из поля status ответа POST.
    Формат: {"status": "Сохранили объявление - <uuid>"}
    """
    return response.json()["status"].split(" - ")[-1].strip()


def _get_item(item_id: str) -> dict:
    """
    Получить объявление по id через GET /api/1/item/:id.
    Возвращает первый элемент массива (API возвращает список).
    """
    response = requests.get(
        f"{BASE_URL}/api/1/item/{item_id}",
        headers=HEADERS_JSON,
    )
    assert response.status_code == 200, (
        f"GET /api/1/item/{item_id} вернул {response.status_code}. Тело: {response.text}"
    )
    data = response.json()
    # API возвращает массив, берём первый элемент
    return data[0] if isinstance(data, list) else data


# Минимальный валидный payload (statistics обязательна!)
def _valid_payload(**kwargs) -> dict:
    base = {
        "sellerID": get_unique_seller_id(),
        "name": "Тестовое объявление",
        "price": 1000,
        "statistics": {"likes": 5, "viewCount": 10, "contacts": 3},
    }
    base.update(kwargs)
    return base


# ─────────────────────────────────────────────
# Позитивные сценарии
# ─────────────────────────────────────────────

@allure.suite("Создание объявления — POST /api/1/item")
@allure.feature("Создание объявления")
@allure.story("Позитивные сценарии")
@allure.title("TC-1.1: Создание объявления с валидными данными (все поля)")
@allure.severity(allure.severity_level.BLOCKER)
def test_create_item_valid_all_fields():
    """
    TC-1.1: POST возвращает {"status": "Сохранили объявление - {uuid}"}.
    Для проверки полей используем GET /api/1/item/:id.
    """
    seller_id = get_unique_seller_id()
    payload = {
        "sellerID": seller_id,
        "name": "Тестовое объявление",
        "price": 1000,
        "statistics": {"likes": 5, "viewCount": 10, "contacts": 3},
    }

    with allure.step("Отправить POST /api/1/item с корректным телом"):
        response = requests.post(
            f"{BASE_URL}/api/1/item",
            json=payload,
            headers=HEADERS_JSON,
        )

    with allure.step("Проверить HTTP-статус 200 OK"):
        assert response.status_code == 200, (
            f"Ожидался статус 200, получен {response.status_code}. Тело: {response.text}"
        )

    with allure.step("Проверить наличие поля 'status' в ответе POST"):
        data = response.json()
        assert "status" in data, f"Ответ не содержит поле 'status'. Тело: {data}"
        assert "Сохранили объявление" in data["status"], (
            f"Неожиданное значение 'status': {data['status']}"
        )

    with allure.step("Извлечь UUID из ответа POST"):
        item_id = _extract_id(response)
        # Проверим, что это валидный UUID
        uuid.UUID(item_id)  # Бросит ValueError, если не UUID

    with allure.step("Получить объявление через GET /api/1/item/:id и проверить поля"):
        item = _get_item(item_id)
        assert item.get("name") == payload["name"], (
            f"name: ожидалось '{payload['name']}', получено '{item.get('name')}'"
        )
        assert item.get("price") == payload["price"], (
            f"price: ожидалось {payload['price']}, получено {item.get('price')}"
        )
        assert "createdAt" in item, "Поле 'createdAt' отсутствует"


@allure.suite("Создание объявления — POST /api/1/item")
@allure.feature("Создание объявления")
@allure.story("Позитивные сценарии")
@allure.title("TC-1.2: Создание объявления без поля statistics — ожидаем 400 (баг API)")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.xfail(
    reason="BUG: statistics является обязательным полем, хотя по документации — необязательное. "
           "API возвращает 400: 'поле likes обязательно'.",
    strict=True,
)
def test_create_item_without_statistics():
    """
    TC-1.2: statistics помечена как необязательная в документации,
    но API отклоняет запрос без неё с 400.
    """
    payload = {
        "sellerID": get_unique_seller_id(),
        "name": "Объявление без статистики",
        "price": 500,
    }

    with allure.step("Отправить POST /api/1/item без поля statistics"):
        response = requests.post(
            f"{BASE_URL}/api/1/item",
            json=payload,
            headers=HEADERS_JSON,
        )

    with allure.step("Ожидаем 200 OK (statistics должна быть необязательной)"):
        assert response.status_code == 200, (
            f"Ожидался статус 200, получен {response.status_code}. Тело: {response.text}"
        )


@allure.suite("Создание объявления — POST /api/1/item")
@allure.feature("Создание объявления")
@allure.story("Позитивные сценарии")
@allure.title("TC-1.3: Создание объявления с price = 0")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.xfail(
    reason="BUG: API отклоняет price=0 с ошибкой 'поле price обязательно'. "
           "Нулевая цена семантически допустима — это falsy-проверка на стороне сервера.",
    strict=True,
)
def test_create_item_price_zero():
    payload = {
        "sellerID": get_unique_seller_id(),
        "name": "Бесплатное объявление",
        "price": 0,
        "statistics": {"likes": 0, "viewCount": 0, "contacts": 0},
    }

    with allure.step("Отправить POST /api/1/item с price = 0"):
        response = requests.post(
            f"{BASE_URL}/api/1/item",
            json=payload,
            headers=HEADERS_JSON,
        )

    with allure.step("Проверить HTTP-статус 200 OK"):
        assert response.status_code == 200, (
            f"Ожидался статус 200, получен {response.status_code}. Тело: {response.text}"
        )


@allure.suite("Создание объявления — POST /api/1/item")
@allure.feature("Создание объявления")
@allure.story("Корнер-кейсы")
@allure.title("TC-1.4: Создание объявления с максимально длинным значением поля name (255 символов)")
@allure.severity(allure.severity_level.NORMAL)
def test_create_item_max_length_name():
    """
    TC-1.4: Поле name со строкой длиной 255 символов является граничным значением.
    Ожидаем, что API примет такое значение и сохранит его без усечения.
    """
    long_name = "А" * 255  
    payload = _valid_payload(name=long_name, price=100)

    with allure.step(f"Сформировать name длиной {len(long_name)} символов"):
        allure.attach(
            long_name,
            name="Значение поля name",
            attachment_type=allure.attachment_type.TEXT,
        )

    with allure.step("Отправить POST /api/1/item с name длиной 255 символов"):
        response = requests.post(
            f"{BASE_URL}/api/1/item",
            json=payload,
            headers=HEADERS_JSON,
        )

    with allure.step("Проверить HTTP-статус 200 OK"):
        assert response.status_code == 200, (
            f"Ожидался статус 200, получен {response.status_code}. Тело: {response.text}"
        )

    with allure.step("Проверить наличие поля 'status' в ответе POST"):
        data = response.json()
        assert "status" in data, f"Ответ не содержит поле 'status'. Тело: {data}"
        assert "Сохранили объявление" in data["status"], (
            f"Неожиданное значение 'status': {data['status']}"
        )

    with allure.step("Извлечь UUID и получить объявление через GET /api/1/item/:id"):
        item_id = _extract_id(response)
        item = _get_item(item_id)

    with allure.step("Проверить, что поле name сохранено без усечения"):
        assert item.get("name") == long_name, (
            f"Ожидалось name длиной {len(long_name)} символов, "
            f"получено '{item.get('name')}' (длина {len(item.get('name', ''))})"
        )

@allure.suite("Создание объявления — POST /api/1/item")
@allure.feature("Создание объявления")
@allure.story("Позитивные сценарии")
@allure.title("TC-1.5: Создание нескольких объявлений с одинаковым sellerId — уникальность id")
@allure.severity(allure.severity_level.CRITICAL)
def test_create_multiple_items_same_seller():
    """TC-1.5: При создании нескольких объявлений с одним sellerId каждое получает уникальный id."""
    seller_id = get_unique_seller_id()
    payload = _valid_payload(sellerID=seller_id, name="Дублирующееся объявление", price=999)

    with allure.step("Создать первое объявление"):
        resp1 = requests.post(f"{BASE_URL}/api/1/item", json=payload, headers=HEADERS_JSON)
    with allure.step("Создать второе объявление с теми же данными"):
        resp2 = requests.post(f"{BASE_URL}/api/1/item", json=payload, headers=HEADERS_JSON)

    with allure.step("Проверить статусы ответов"):
        assert resp1.status_code == 200, f"Первый запрос: ожидался 200, получен {resp1.status_code}"
        assert resp2.status_code == 200, f"Второй запрос: ожидался 200, получен {resp2.status_code}"

    id1 = _extract_id(resp1)
    id2 = _extract_id(resp2)

    with allure.step("Убедиться, что id двух объявлений различаются"):
        assert id1 != id2, (
            f"Ожидались разные id, но оба равны '{id1}'. "
            "POST /api/1/item должен создавать новое уникальное объявление каждый раз."
        )


@allure.suite("Создание объявления — POST /api/1/item")
@allure.feature("Создание объявления")
@allure.story("Позитивные сценарии")
@allure.title("TC-1.6: Создание объявления с нулевыми значениями statistics")
@allure.severity(allure.severity_level.NORMAL)
def test_create_item_zero_statistics():
    """TC-1.6: Нулевые значения внутри statistics (0 для каждого поля) допустимы."""
    payload = {
        "sellerID": get_unique_seller_id(),
        "name": "Нулевая статистика",
        "price": 200,
        "statistics": {"likes": 0, "viewCount": 0, "contacts": 0},
    }

    with allure.step("Отправить запрос с нулевыми значениями statistics"):
        response = requests.post(
            f"{BASE_URL}/api/1/item",
            json=payload,
            headers=HEADERS_JSON,
        )

    with allure.step("Проверить HTTP-статус 200 OK"):
        assert response.status_code == 200, (
            f"Ожидался статус 200, получен {response.status_code}. Тело: {response.text}"
        )

    with allure.step("Проверить, что ответ содержит поле 'status'"):
        assert "status" in response.json(), "Поле 'status' отсутствует в ответе"


# ─────────────────────────────────────────────
# Негативные сценарии
# ─────────────────────────────────────────────

@allure.suite("Создание объявления — POST /api/1/item")
@allure.feature("Создание объявления")
@allure.story("Негативные сценарии")
@allure.title("TC-1.7: Создание объявления без обязательного поля name")
@allure.severity(allure.severity_level.CRITICAL)
def test_create_item_missing_name():
    """TC-1.7: Запрос без поля 'name' должен вернуть 400 Bad Request."""
    payload = {
        "sellerID": get_unique_seller_id(),
        "price": 100,
        "statistics": {"likes": 1, "viewCount": 1, "contacts": 1},
    }

    with allure.step("Отправить POST /api/1/item без поля 'name'"):
        response = requests.post(
            f"{BASE_URL}/api/1/item",
            json=payload,
            headers=HEADERS_JSON,
        )

    with allure.step("Проверить HTTP-статус 400 Bad Request"):
        assert response.status_code == 400, (
            f"Ожидался статус 400, получен {response.status_code}. Тело: {response.text}"
        )


@allure.suite("Создание объявления — POST /api/1/item")
@allure.feature("Создание объявления")
@allure.story("Негативные сценарии")
@allure.title("TC-1.8: Создание объявления без обязательного поля price")
@allure.severity(allure.severity_level.CRITICAL)
def test_create_item_missing_price():
    """TC-1.8: Запрос без поля 'price' должен вернуть 400 Bad Request."""
    payload = {
        "sellerID": get_unique_seller_id(),
        "name": "Без цены",
        "statistics": {"likes": 1, "viewCount": 1, "contacts": 1},
    }

    with allure.step("Отправить POST /api/1/item без поля 'price'"):
        response = requests.post(
            f"{BASE_URL}/api/1/item",
            json=payload,
            headers=HEADERS_JSON,
        )

    with allure.step("Проверить HTTP-статус 400 Bad Request"):
        assert response.status_code == 400, (
            f"Ожидался статус 400, получен {response.status_code}. Тело: {response.text}"
        )


@allure.suite("Создание объявления — POST /api/1/item")
@allure.feature("Создание объявления")
@allure.story("Негативные сценарии")
@allure.title("TC-1.9: Создание объявления без обязательного поля sellerId")
@allure.severity(allure.severity_level.CRITICAL)
def test_create_item_missing_seller_id():
    """TC-1.9: Запрос без поля 'sellerId' должен вернуть 400 Bad Request."""
    payload = {
        "name": "Без продавца",
        "price": 300,
        "statistics": {"likes": 1, "viewCount": 1, "contacts": 1},
    }

    with allure.step("Отправить POST /api/1/item без поля 'sellerId'"):
        response = requests.post(
            f"{BASE_URL}/api/1/item",
            json=payload,
            headers=HEADERS_JSON,
        )

    with allure.step("Проверить HTTP-статус 400 Bad Request"):
        assert response.status_code == 400, (
            f"Ожидался статус 400, получен {response.status_code}. Тело: {response.text}"
        )


@allure.suite("Создание объявления — POST /api/1/item")
@allure.feature("Создание объявления")
@allure.story("Негативные сценарии")
@allure.title("TC-1.10: Создание объявления с отрицательной ценой")
@allure.severity(allure.severity_level.CRITICAL)
def test_create_item_negative_price():
    """TC-1.10: Отрицательная цена должна быть отклонена (ожидаем 400)."""
    payload = _valid_payload(name="Отрицательная цена", price=-500)

    with allure.step("Отправить POST /api/1/item с price = -500"):
        response = requests.post(
            f"{BASE_URL}/api/1/item",
            json=payload,
            headers=HEADERS_JSON,
        )

    with allure.step("Проверить HTTP-статус 400 Bad Request"):
        assert response.status_code == 400, (
            f"Ожидался статус 400, получен {response.status_code}. Тело: {response.text}"
        )


@allure.suite("Создание объявления — POST /api/1/item")
@allure.feature("Создание объявления")
@allure.story("Негативные сценарии")
@allure.title("TC-1.11: Создание объявления с типом price = строка")
@allure.severity(allure.severity_level.CRITICAL)
def test_create_item_price_as_string():
    """TC-1.11: Нечисловое значение в поле 'price' должно быть отклонено (ожидаем 400)."""
    payload = _valid_payload(name="Строка в цене", price="сто рублей")

    with allure.step("Отправить POST /api/1/item с price в виде строки"):
        response = requests.post(
            f"{BASE_URL}/api/1/item",
            json=payload,
            headers=HEADERS_JSON,
        )

    with allure.step("Проверить HTTP-статус 400 Bad Request"):
        assert response.status_code == 400, (
            f"Ожидался статус 400, получен {response.status_code}. Тело: {response.text}"
        )


@allure.suite("Создание объявления — POST /api/1/item")
@allure.feature("Создание объявления")
@allure.story("Негативные сценарии")
@allure.title("TC-1.12: Создание объявления с пустым телом запроса")
@allure.severity(allure.severity_level.CRITICAL)
def test_create_item_empty_body():
    """TC-1.12: Пустое тело запроса должно вернуть 400 Bad Request."""
    with allure.step("Отправить POST /api/1/item с пустым телом {}"):
        response = requests.post(
            f"{BASE_URL}/api/1/item",
            json={},
            headers=HEADERS_JSON,
        )

    with allure.step("Проверить HTTP-статус 400 Bad Request"):
        assert response.status_code == 400, (
            f"Ожидался статус 400, получен {response.status_code}. Тело: {response.text}"
        )

@allure.suite("Создание объявления — POST /api/1/item")
@allure.feature("Создание объявления")
@allure.story("Негативные сценарии")
@allure.title("TC-1.13: Создание объявления с sellerID вне допустимого диапазона (слишком большое)")
@allure.severity(allure.severity_level.CRITICAL)
def test_create_item_seller_id_too_large():
    """
    TC-1.13: sellerID = 9999999999 значительно превышает допустимый диапазон
    (INT32_MAX = 2147483647). Ожидаем, что API отклонит запрос с 400 Bad Request.

    Примечание: если API хранит sellerID как INT32, значение 9999999999
    не поместится в тип — это должно приводить к ошибке валидации.
    """
    oversized_seller_id = 9_999_999_999 
    payload = _valid_payload(
        sellerID=oversized_seller_id,
        name="Огромный sellerID",
        price=100,
    )

    with allure.step(f"Отправить POST /api/1/item с sellerID = {oversized_seller_id}"):
        response = requests.post(
            f"{BASE_URL}/api/1/item",
            json=payload,
            headers=HEADERS_JSON,
        )

    with allure.step("Проверить HTTP-статус 400 Bad Request"):
        assert response.status_code == 400, (
            f"Ожидался статус 400, получен {response.status_code}. Тело: {response.text}"
        )

    with allure.step("Проверить наличие информативного сообщения об ошибке в теле ответа"):
        try:
            error_body = response.json()
            assert error_body, "Тело ответа с ошибкой не должно быть пустым"
        except ValueError:
            # Если ответ не JSON — достаточно статуса 400
            pass


@allure.suite("Создание объявления — POST /api/1/item")
@allure.feature("Создание объявления")
@allure.story("Негативные сценарии")
@allure.title("TC-1.14: Создание объявления с отрицательным sellerId")
@allure.severity(allure.severity_level.CRITICAL)
def test_create_item_negative_seller_id():
    """TC-1.14: Отрицательный sellerId должен быть отклонён (ожидаем 400)."""
    payload = _valid_payload(sellerID=-111111, name="Отрицательный sellerId")

    with allure.step("Отправить POST /api/1/item с sellerId = -111111"):
        response = requests.post(
            f"{BASE_URL}/api/1/item",
            json=payload,
            headers=HEADERS_JSON,
        )

    with allure.step("Проверить HTTP-статус 400 Bad Request"):
        assert response.status_code == 400, (
            f"Ожидался статус 400, получен {response.status_code}. Тело: {response.text}"
        )


@allure.suite("Создание объявления — POST /api/1/item")
@allure.feature("Создание объявления")
@allure.story("Негативные сценарии")
@allure.title("TC-1.15: Создание объявления с name = пустая строка")
@allure.severity(allure.severity_level.CRITICAL)
def test_create_item_empty_name():
    """TC-1.15: Пустая строка в поле 'name' должна вернуть 400 Bad Request."""
    payload = _valid_payload(name="")

    with allure.step("Отправить POST /api/1/item с name = ''"):
        response = requests.post(
            f"{BASE_URL}/api/1/item",
            json=payload,
            headers=HEADERS_JSON,
        )

    with allure.step("Проверить HTTP-статус 400 Bad Request"):
        assert response.status_code == 400, (
            f"Ожидался статус 400, получен {response.status_code}. Тело: {response.text}"
        )


@allure.suite("Создание объявления — POST /api/1/item")
@allure.feature("Создание объявления")
@allure.story("Негативные сценарии")
@allure.title("TC-1.16: Создание объявления с price = null")
@allure.severity(allure.severity_level.CRITICAL)
def test_create_item_price_null():
    """TC-1.16: Значение null в поле 'price' должно вернуть 400 Bad Request."""
    payload = _valid_payload(name="Нулл в цене", price=None)

    with allure.step("Отправить POST /api/1/item с price = null"):
        response = requests.post(
            f"{BASE_URL}/api/1/item",
            json=payload,
            headers=HEADERS_JSON,
        )

    with allure.step("Проверить HTTP-статус 400 Bad Request"):
        assert response.status_code == 400, (
            f"Ожидался статус 400, получен {response.status_code}. Тело: {response.text}"
        )


# ─────────────────────────────────────────────
# Корнер-кейсы и граничные значения
# ─────────────────────────────────────────────

@allure.suite("Создание объявления — POST /api/1/item")
@allure.feature("Создание объявления")
@allure.story("Корнер-кейсы")
@allure.title("TC-1.17: Идемпотентность: два одинаковых POST-запроса создают разные объявления")
@allure.severity(allure.severity_level.CRITICAL)
def test_create_item_not_idempotent():
    """TC-1.17: POST /api/1/item НЕ является идемпотентным — создаёт новое объявление при каждом вызове."""
    seller_id = get_unique_seller_id()
    payload = _valid_payload(sellerID=seller_id, name="Идемпотентность", price=100)

    with allure.step("Выполнить первый POST-запрос"):
        resp1 = requests.post(f"{BASE_URL}/api/1/item", json=payload, headers=HEADERS_JSON)
    with allure.step("Выполнить второй идентичный POST-запрос"):
        resp2 = requests.post(f"{BASE_URL}/api/1/item", json=payload, headers=HEADERS_JSON)

    with allure.step("Проверить статусы"):
        assert resp1.status_code == 200
        assert resp2.status_code == 200

    id1 = _extract_id(resp1)
    id2 = _extract_id(resp2)

    with allure.step("Убедиться, что id двух объявлений отличаются (POST не идемпотентен)"):
        assert id1 != id2, f"Ожидались разные id, но оба равны '{id1}'"


@allure.suite("Создание объявления — POST /api/1/item")
@allure.feature("Создание объявления")
@allure.story("Корнер-кейсы")
@allure.title("TC-1.18: Создание объявления с price = INT32_MAX (2147483647)")
@allure.severity(allure.severity_level.NORMAL)
def test_create_item_max_price():
    """TC-1.18: Граничное значение price = INT32_MAX (2147483647)."""
    payload = _valid_payload(name="Максимальная цена", price=2147483647)

    with allure.step("Отправить POST /api/1/item с price = 2147483647"):
        response = requests.post(
            f"{BASE_URL}/api/1/item",
            json=payload,
            headers=HEADERS_JSON,
        )

    with allure.step("Проверить HTTP-статус 200 OK"):
        assert response.status_code == 200, (
            f"Ожидался статус 200, получен {response.status_code}. Тело: {response.text}"
        )

    with allure.step("Получить объявление через GET и проверить price"):
        item_id = _extract_id(response)
        item = _get_item(item_id)
        assert item.get("price") == 2147483647, (
            f"Ожидалось price=2147483647, получено {item.get('price')}"
        )


@allure.suite("Создание объявления — POST /api/1/item")
@allure.feature("Создание объявления")
@allure.story("Корнер-кейсы")
@allure.title("TC-1.19: Создание объявления с price = дробное число (float)")
@allure.severity(allure.severity_level.NORMAL)
def test_create_item_float_price():
    """TC-1.19: Проверка поведения при передаче float в поле price."""
    payload = _valid_payload(name="Дробная цена", price=99.99)

    with allure.step("Отправить POST /api/1/item с price = 99.99 (float)"):
        response = requests.post(
            f"{BASE_URL}/api/1/item",
            json=payload,
            headers=HEADERS_JSON,
        )

    with allure.step("Проверить, что статус 400 (если price только integer) или 200 (если float допустим)"):
        assert response.status_code in (200, 400), (
            f"Получен неожиданный статус: {response.status_code}. Тело: {response.text}"
        )


@allure.suite("Создание объявления — POST /api/1/item")
@allure.feature("Создание объявления")
@allure.story("Корнер-кейсы")
@allure.title("TC-1.20: Создание объявления с спецсимволами и эмодзи в поле name")
@allure.severity(allure.severity_level.MINOR)
def test_create_item_special_chars_in_name():
    """TC-1.20: Поле name с Unicode-символами и эмодзи должно обрабатываться без потерь."""
    name_with_special = 'Объявление 🚗 <test> & "кавычки"'
    payload = _valid_payload(name=name_with_special)

    with allure.step("Отправить POST /api/1/item с спецсимволами в name"):
        response = requests.post(
            f"{BASE_URL}/api/1/item",
            json=payload,
            headers=HEADERS_JSON,
        )

    with allure.step("Проверить HTTP-статус 200 OK"):
        assert response.status_code == 200, (
            f"Ожидался статус 200, получен {response.status_code}. Тело: {response.text}"
        )

    with allure.step("Получить объявление через GET и проверить name"):
        item_id = _extract_id(response)
        item = _get_item(item_id)
        assert item.get("name") == name_with_special, (
            f"Ожидалось name='{name_with_special}', получено '{item.get('name')}'"
        )


# ─────────────────────────────────────────────
# Функциональные и нефункциональные проверки
# ─────────────────────────────────────────────

@allure.suite("Создание объявления — POST /api/1/item")
@allure.feature("Создание объявления")
@allure.story("Негативные сценарии")
@allure.title("TC-1.21: Создание объявления с неверным Content-Type (text/plain)")
@allure.severity(allure.severity_level.NORMAL)
def test_create_item_wrong_content_type():
    """
    TC-1.21: Запрос с Content-Type: text/plain и корректным JSON-телом должен
    быть отклонён. Ожидаемые статусы: 400 Bad Request или 415 Unsupported Media Type.

    Если сервер принимает запрос (200) — это потенциальная проблема,
    так как тип контента не проверяется должным образом.
    """
    # Формируем корректный JSON как строку, но с неверным Content-Type
    import json as _json

    payload_dict = _valid_payload(name="Неверный Content-Type", price=100)
    raw_body = _json.dumps(payload_dict, ensure_ascii=False)

    wrong_content_type_headers = {
        **HEADERS_JSON,
        "Content-Type": "text/plain",
    }

    with allure.step("Сформировать заголовки с Content-Type: text/plain"):
        allure.attach(
            str(wrong_content_type_headers),
            name="Заголовки запроса",
            attachment_type=allure.attachment_type.TEXT,
        )

    with allure.step("Отправить POST /api/1/item с Content-Type: text/plain и корректным JSON-телом"):
        response = requests.post(
            f"{BASE_URL}/api/1/item",
            data=raw_body.encode("utf-8"),   # передаём тело как сырые байты
            headers=wrong_content_type_headers,
        )

    with allure.step(
        "Проверить HTTP-статус: ожидается 400 Bad Request или 415 Unsupported Media Type"
    ):
        assert response.status_code in (400, 415), (
            f"Ожидался статус 400 или 415, получен {response.status_code}. "
            f"Тело: {response.text}\n"
            "Примечание: статус 200 означает, что сервер игнорирует Content-Type — "
            "потенциальная проблема безопасности/контракта."
        )


@allure.suite("Создание объявления — POST /api/1/item")
@allure.feature("Создание объявления")
@allure.story("Функциональные проверки")
@allure.title("TC-1.22: Проверка структуры ответа при успешном создании объявления")
@allure.severity(allure.severity_level.CRITICAL)
def test_create_item_response_schema():
    """
    TC-1.22: POST возвращает только {status}.
    Полная схема проверяется через GET /api/1/item/:id.
    """
    payload = _valid_payload(name="Проверка схемы", price=750)

    with allure.step("Отправить POST /api/1/item"):
        response = requests.post(
            f"{BASE_URL}/api/1/item",
            json=payload,
            headers=HEADERS_JSON,
        )

    assert response.status_code == 200
    post_data = response.json()

    with allure.step("Проверить структуру ответа POST — только поле 'status'"):
        assert "status" in post_data, "Поле 'status' отсутствует в ответе POST"

    item_id = _extract_id(response)

    with allure.step("Получить объявление через GET /api/1/item/:id"):
        item = _get_item(item_id)

    with allure.step("Проверить наличие обязательных полей: id, sellerId, name, price, statistics, createdAt"):
        for field in ("id", "sellerId", "name", "price", "statistics", "createdAt"):
            assert field in item, f"Поле '{field}' отсутствует в ответе GET"

    with allure.step("Проверить тип поля 'id' — строка"):
        assert isinstance(item["id"], str), (
            f"Поле 'id' должно быть строкой, получено {type(item['id'])}"
        )

    with allure.step("Проверить тип поля 'price' — число"):
        assert isinstance(item["price"], (int, float)), (
            f"Поле 'price' должно быть числом, получено {type(item['price'])}"
        )

    with allure.step("Проверить структуру поля 'statistics'"):
        stats = item["statistics"]
        assert isinstance(stats, dict), f"Поле 'statistics' должно быть объектом"
        for stat_field in ("likes", "viewCount", "contacts"):
            assert stat_field in stats, f"Поле 'statistics.{stat_field}' отсутствует"


@allure.suite("Создание объявления — POST /api/1/item")
@allure.feature("Создание объявления")
@allure.story("Нефункциональные проверки")
@allure.title("TC-1.23: Проверка времени ответа при создании объявления (< 2000 мс)")
@allure.severity(allure.severity_level.MINOR)
def test_create_item_response_time():
    """TC-1.23: Время ответа на создание объявления не должно превышать 2000 мс."""
    payload = _valid_payload(name="Проверка производительности", price=1)

    with allure.step("Отправить POST /api/1/item и замерить время ответа"):
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/api/1/item",
            json=payload,
            headers=HEADERS_JSON,
        )
        elapsed_ms = (time.time() - start) * 1000

    assert response.status_code == 200, (
        f"Ожидался статус 200, получен {response.status_code}. Тело: {response.text}"
    )

    with allure.step(f"Проверить, что время ответа < 2000 мс (фактически: {elapsed_ms:.0f} мс)"):
        assert elapsed_ms < 2000, (
            f"Время ответа {elapsed_ms:.0f} мс превышает допустимые 2000 мс"
        )


@allure.suite("Создание объявления — POST /api/1/item")
@allure.feature("Создание объявления")
@allure.story("Нефункциональные проверки")
@allure.title("TC-1.24: Проверка заголовка Content-Type в ответе")
@allure.severity(allure.severity_level.NORMAL)
def test_create_item_content_type_header():
    """TC-1.24: Ответ должен возвращаться с заголовком Content-Type: application/json."""
    payload = _valid_payload(name="Проверка заголовков", price=1)

    with allure.step("Отправить POST /api/1/item"):
        response = requests.post(
            f"{BASE_URL}/api/1/item",
            json=payload,
            headers=HEADERS_JSON,
        )

    assert response.status_code == 200, (
        f"Ожидался статус 200, получен {response.status_code}. Тело: {response.text}"
    )

    with allure.step("Проверить заголовок Content-Type содержит 'application/json'"):
        content_type = response.headers.get("Content-Type", "")
        assert "application/json" in content_type, (
            f"Ожидался Content-Type: application/json, получен: '{content_type}'"
        )