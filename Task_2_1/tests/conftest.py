"""
Конфигурация и общие фикстуры для pytest.
Используется библиотека allure для формирования отчётов.
"""

import random
import pytest
import requests
import allure

BASE_URL = "https://qa-internship.avito.com"
HEADERS_JSON = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}


def get_unique_seller_id() -> int:
    """Генерация уникального sellerID в диапазоне 111111–999999."""
    return random.randint(111111, 999999)


@pytest.fixture(scope="session")
def base_url() -> str:
    """Базовый URL сервиса."""
    return BASE_URL


@pytest.fixture(scope="session")
def headers() -> dict:
    """Общие заголовки для JSON-запросов."""
    return HEADERS_JSON


@pytest.fixture
def unique_seller_id() -> int:
    """Уникальный sellerID для каждого теста."""
    return get_unique_seller_id()


@pytest.fixture
def created_item(base_url, headers, unique_seller_id):
    """
    Фикстура: создаёт объявление перед тестом и возвращает данные ответа.
    Используется для тестов, которым нужно существующее объявление.

    ИСПРАВЛЕНИЕ: сервер возвращает {"status": "Сохранено - <UUID>"}.
    Поля "id" в ответе нет — извлекаем UUID из строки status и
    добавляем его в словарь под ключом "id" для удобства тестов.
    """
    payload = {
        "sellerID": unique_seller_id,
        "name": "Тестовое объявление (фикстура)",
        "price": 1000,
        "statistics": {
            "likes": 5,
            "viewCount": 10,
            "contacts": 3,
        },
    }
    with allure.step("Предусловие: создать объявление через POST /api/1/item"):
        response = requests.post(
            f"{base_url}/api/1/item",
            json=payload,
            headers=headers,
        )
    assert response.status_code == 200, (
        f"Не удалось создать объявление: {response.status_code} {response.text}"
    )
    data = response.json()

    item_id = data["status"].split(" - ")[-1].strip()
    assert item_id, "Не удалось извлечь id объявления из поля status"
    data["id"] = item_id 

    return data


@pytest.fixture
def created_item_with_stats(base_url, headers, unique_seller_id):
    """
    Фикстура: создаёт объявление с конкретными значениями статистики.
    Используется для тестов статистики.

    ИСПРАВЛЕНИЕ: убран assert "id" in data — поля "id" в ответе нет.
    """
    payload = {
        "sellerID": unique_seller_id,
        "name": "Объявление для тестирования статистики",
        "price": 500,
        "statistics": {
            "likes": 7,
            "viewCount": 15,
            "contacts": 3,
        },
    }
    with allure.step("Предусловие: создать объявление со статистикой"):
        response = requests.post(
            f"{base_url}/api/1/item",
            json=payload,
            headers=headers,
        )
    assert response.status_code == 200
    data = response.json()

    item_id = data["status"].split(" - ")[-1].strip()
    assert item_id, "Не удалось извлечь id объявления из поля status"
    data["id"] = item_id

    return data