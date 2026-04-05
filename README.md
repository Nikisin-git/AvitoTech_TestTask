# Тестовое задание Avito QA Internship 2026 — Задание 2.1: Тесты API

Автоматизированные тесты для API сервиса объявлений.  
**Хост:** `https://qa-internship.avito.com`  
**Язык:** Python 3.8+  
**Фреймворк:** pytest + allure-pytest  

---

## Структура проекта

```


AvitoTech_TestTask
│
├──Task_1 - папка задания 1
│      ├──BUGS_FROM_SCREENSHOT.md - файл с описанием найденных багов 
│      └──Img                     - папка со скриншотами багов
│
├──Task_2_1  - папка задания 2
│    ├── tests/          - Директория с автотестами      
│       ├── conftest.py                 - Общие фикстуры и конфигурация pytest
│       ├── test_create_item.py         - Тест-сьют 1: POST /api/1/item (создание объявления)
│       ├── test_get_item.py            - Тест-сьют 2: GET /api/1/item/:id (получение по id)
│       ├── test_get_seller_items.py    - Тест-сьют 3: GET /api/1/:sellerID/item (объявления продавца)
│       └── test_get_statistic.py       - Тест-сьют 4: GET /api/1/statistic/:id (статистика)
│   
│    ├──BUGS.md          - Баг-репорты, обнаруженные в ходе тестирования
│    ├──pyproject.toml   - Конфигурация black
│    ├──pytest.ini       - Конфигурация pytest
│    ├──setup.cfg        - Конфигурация flake8 и isort
│    └──TESTCASES.md     - Полное описание тест-кейсов  
│        
├── README.md          - Описание проекта и инструкция по развертыванию
└── requirements.txt   - Зависимости Python
    
    
```

---

## Описание тестируемых ручек API

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| `POST` | `/api/1/item` | Создать объявление |
| `GET` | `/api/1/item/:id` | Получить объявление по его идентификатору |
| `GET` | `/api/1/:sellerID/item` | Получить все объявления по идентификатору продавца |
| `GET` | `/api/1/statistic/:id` | Получить статистику по item id |

---

## Быстрый старт

### Шаг 1: Клонировать репозиторий

```bash
git clone <URL репозитория>
cd AvitoTech_TestTask
```

Или скачайте ZIP-архив и распакуйте его.

---

### Шаг 2: Убедиться, что Python установлен

```bash
python --version
# или
python3 --version
```

Требуется Python **3.8 или выше**. Скачать можно на [python.org](https://www.python.org/downloads/).

> **Windows:** При установке Python поставьте галочку «Add python.exe to PATH».

---

### Шаг 3: Создать и активировать виртуальное окружение (рекомендуется)

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (CMD):**
```cmd
python -m venv (полный_путь к_корневой_папке_проекта)\venv
.venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
python -m venv (полный_путь к_корневой_папке_проекта)\venv
.venv\Scripts\Activate.ps1
```

---

### Шаг 4: Установить зависимости

```bash
pip install -r requirements.txt
```

Если не работает, попробуйте:
```bash
pip3 install -r requirements.txt
```

---

### Шаг 5: Установить Allure CLI (для генерации отчётов)

**macOS (через Homebrew):**
```bash
brew install allure
```

**Windows (через Scoop):**

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression
```

```powershell
scoop install allure
```

**Linux:**
```bash
sudo apt-add-repository ppa:qameta/allure
sudo apt-get update
sudo apt-get install allure
```

Или скачайте с [официального сайта](https://allurereport.org/docs/install/).

---

## Запуск автотестов

### Запуск всех тестов

```bash
pytest
```

### Запуск всех тестов с подробным выводом

```bash
pytest -v
```

### Запуск тестов с генерацией Allure-отчёта

```bash
pytest --alluredir=allure-results
allure generate allure-results -o allure-report --clean
allure open allure-report
```

### Запуск тестов с HTML-отчётом (без Allure CLI)

```bash
pytest --html=report.html --self-contained-html
```

---

## Запуск отдельных тест-сьютов

### Тест-сьют 1: Создание объявления (`POST /api/1/item`)

```bash
pytest Task_2_1/tests/test_create_item.py -v
```

### Тест-сьют 2: Получение объявления по id (`GET /api/1/item/:id`)

```bash
pytest Task_2_1/tests/test_get_item.py -v
```

### Тест-сьют 3: Объявления продавца (`GET /api/1/:sellerID/item`)

```bash
pytest Task_2_1/tests/test_get_seller_items.py -v
```

### Тест-сьют 4: Статистика объявления (`GET /api/1/statistic/:id`)

```bash
pytest Task_2_1/tests/test_get_statistic.py -v
```

---

## Запуск отдельных тестов по имени функции

```bash
# Запуск конкретного теста
pytest tests/test_create_item.py::test_create_item_valid_all_fields -v
```

---

## Запуск отдельных тестов по номеру тест-кейса (TC)

| Тест-кейс | Название теста | Команда запуска |
|-----------|----------------|-----------------|
| TC-1.1 | Создание объявления с валидными данными (все поля) | `pytest Task_2_1/tests/test_create_item.py::test_create_item_valid_all_fields -v` |
| TC-1.2 | Создание объявления без поля statistics | `pytest Task_2_1/tests/test_create_item.py::test_create_item_without_statistics -v` |
| TC-1.3 | Создание объявления с price = 0 | `pytest Task_2_1/tests/test_create_item.py::test_create_item_price_zero -v` |
| TC-1.4 | Создание объявления с максимально длинным значением поля name | `pytest Task_2_1/tests/test_create_item.py::test_create_item_max_length_name -v` |
| TC-1.5 | Создание нескольких объявлений с одинаковым sellerID | `pytest Task_2_1/tests/test_create_item.py::test_create_multiple_items_same_seller -v` |
| TC-1.6 | Создание объявления с нулевыми значениями в statistics | `pytest Task_2_1/tests/test_create_item.py::test_create_item_zero_statistics -v` |
| TC-1.7 | Создание объявления без обязательного поля name| `pytest Task_2_1/tests/test_create_item.py::test_create_item_missing_name -v` |
| TC-1.8 | Создание объявления без обязательного поля price | `pytest Task_2_1/tests/test_create_item.py::test_create_item_missing_price -v` |
| TC-1.9 | Создание объявления без обязательного поля sellerID | `pytest Task_2_1/tests/test_create_item.py::test_create_item_missing_seller_id -v` |
| TC-1.10 | Создание объявления с отрицательной ценой | `pytest Task_2_1/tests/test_create_item.py::test_create_item_negative_price -v` |
| TC-1.11 | Создание объявления с типом price = строка | `pytest Task_2_1/tests/test_create_item.py::test_create_item_price_as_string -v` |
| TC-1.12 | Создание объявления с пустым телом запроса | `pytest Task_2_1/tests/test_create_item.py::test_create_item_empty_body -v` |
| TC-1.13 | Создание объявления с sellerID вне допустимого диапазона (слишком большое) | `pytest Task_2_1/tests/test_create_item.py::test_create_item_seller_id_too_large -v` |
| TC-1.14 | Создание объявления с отрицательным sellerID | `pytest Task_2_1/tests/test_create_item.py::test_create_item_negative_seller_id -v` |
| TC-1.15 | Создание объявления с name = пустая строка | `pytest Task_2_1/tests/test_create_item.py::test_create_item_empty_name -v` |
| TC-1.16 | Создание объявления с price = null | `pytest Task_2_1/tests/test_create_item.py::test_create_item_price_null -v` |
| TC-1.17 | Создание двух идентичных объявлений (проверка идемпотентности) | `pytest Task_2_1/tests/test_create_item.py::test_create_item_not_idempotent -v` |
| TC-1.18 | Создание объявления с price = максимальное целое число (int32 max: 2147483647) | `pytest Task_2_1/tests/test_create_item.py::test_create_item_max_price -v` |
| TC-1.19 | Создание объявления с price = значение float | `pytest Task_2_1/tests/test_create_item.py::test_create_item_float_price -v` |
| TC-1.20 | Создание объявления с name, содержащим спецсимволы и эмодзи | `pytest Task_2_1/tests/test_create_item.py::test_create_item_special_chars_in_name -v` |
| TC-1.21 | Создание объявления с неверным Content-Type | `pytest Task_2_1/tests/test_create_item.py::test_create_item_wrong_content_type -v` |
| TC-1.22 | Проверка структуры ответа при успешном создании объявления | `pytest Task_2_1/tests/test_create_item.py::test_create_item_response_schema -v` |
| TC-1.23 | Проверка времени ответа при создании объявления | `pytest Task_2_1/tests/test_create_item.py::test_create_item_response_time -v` |
| TC-1.24 | Проверка заголовка Content-Type в ответе | `pytest Task_2_1/tests/test_create_item.py::test_create_item_content_type_header -v` |
| TC-2.1 | Получение объявления по существующему id | `pytest Task_2_1/tests/test_get_item.py::test_get_item_by_existing_id -v` |
| TC-2.2 | Соответствие полей ответа данным созданного объявления (E2E) | `pytest Task_2_1/tests/test_get_item.py::test_get_item_fields_match_created -v` |
| TC-2.3 | Проверка структуры ответа при получении объявления | `pytest Task_2_1/tests/test_get_item.py::test_get_item_response_schema -v` |
| TC-2.4 | Получение объявления по несуществующему id | `pytest Task_2_1/tests/test_get_item.py::test_get_item_not_found -v` |
| TC-2.5 | Получение объявления с невалидным форматом id (не UUID) | `pytest Task_2_1/tests/test_get_item.py::test_get_item_invalid_id_format -v` |
| TC-2.6 | Получение объявления с числом вместо UUID в id | `pytest Task_2_1/tests/test_get_item.py::test_get_item_numeric_id -v` |
| TC-2.7 | Получение объявления с пустым id | `pytest Task_2_1/tests/test_get_item.py::test_get_item_empty_id -v` |
| TC-2.8 | Идемпотентность GET-запроса по id | `pytest Task_2_1/tests/test_get_item.py::test_get_item_idempotent -v` |
| TC-2.9 | Получение объявления с UUID в верхнем регистре | `pytest Task_2_1/tests/test_get_item.py::test_get_item_uppercase_uuid -v` |
| TC-2.10 | Проверка времени ответа при получении объявления по id | `pytest Task_2_1/tests/test_get_item.py::test_get_item_response_time -v` |
| TC-2.11 | Проверка заголовка Content-Type в ответе | `pytest Task_2_1/tests/test_get_item.py::test_get_item_content_type_header -v` |
| TC-3.1 | Получение объявлений по существующему sellerID | `pytest Task_2_1/tests/test_get_seller_items.py::test_get_items_by_seller_id_existing -v` |
| TC-3.2 | E2E: Создать объявление и найти его в списке объявлений продавца | `pytest Task_2_1/tests/test_get_seller_items.py::test_get_seller_items_contains_created -v` |
| TC-3.3 | Получение нескольких объявлений одного продавца | `pytest Task_2_1/tests/test_get_seller_items.py::test_get_seller_items_multiple -v` |
| TC-3.4 | Получение объявлений по sellerID, у которого нет объявлений | `pytest Task_2_1/tests/test_get_seller_items.py::test_get_seller_items_empty_seller -v` |
| TC-3.5 | Получение объявлений с sellerID = строка (не число) | `pytest Task_2_1/tests/test_get_seller_items.py::test_get_seller_items_string_seller_id -v` |
| TC-3.6 | Получение объявлений с отрицательным sellerID | `pytest Task_2_1/tests/test_get_seller_items.py::test_get_seller_items_negative_seller_id -v` |
| TC-3.7 | Получение объявлений с sellerID = 0 | `pytest Task_2_1/tests/test_get_seller_items.py::test_get_seller_items_zero_seller_id -v` |
| TC-3.8 | Получение объявлений с очень большим sellerID | `pytest Task_2_1/tests/test_get_seller_items.py::test_get_seller_items_very_large_seller_id -v` |
| TC-3.9 | Идемпотентность GET-запроса по sellerID | `pytest Task_2_1/tests/test_get_seller_items.py::test_get_seller_items_idempotent -v` |
| TC-3.10 | Проверка, что объявления другого продавца не попадают в ответ | `pytest Task_2_1/tests/test_get_seller_items.py::test_get_seller_items_data_isolation -v` |
| TC-3.11 | Проверка времени ответа при получении объявлений продавца | `pytest Task_2_1/tests/test_get_seller_items.py::test_get_seller_items_response_time -v` |
| TC-3.12 | Проверка структуры элементов в ответе | `pytest Task_2_1/tests/test_get_seller_items.py::test_get_seller_items_schema -v` |
| TC-4.1 | Получение статистики по существующему id объявления | `pytest Task_2_1/tests/test_get_statistic.py::test_get_statistic_existing_id -v` |
| TC-4.2 | E2E: Создать объявление с конкретной статистикой и получить её | `pytest Task_2_1/tests/test_get_statistic.py::test_get_statistic_values_match_created -v` |
| TC-4.3 | Проверка структуры ответа статистики | `pytest Task_2_1/tests/test_get_statistic.py::test_get_statistic_response_schema -v` |
| TC-4.4 | Получение статистики по несуществующему id | `pytest Task_2_1/tests/test_get_statistic.py::test_get_statistic_not_found -v` |
| TC-4.5 | Получение статистики с невалидным форматом id | `pytest Task_2_1/tests/test_get_statistic.py::test_get_statistic_invalid_id_format -v` |
| TC-4.6 | Получение статистики с числом вместо UUID | `pytest Task_2_1/tests/test_get_statistic.py::test_get_statistic_numeric_id -v` |
| TC-4.7 | Идемпотентность GET-запроса на статистику | `pytest Task_2_1/tests/test_get_statistic.py::test_get_statistic_idempotent -v` |
| TC-4.8 | Проверка, что статистика объявления не пересекается с другим объявлением | `pytest Task_2_1/tests/test_get_statistic.py::test_get_statistic_isolation -v` |
| TC-4.9 | Проверка времени ответа при запросе статистики | `pytest Task_2_1/tests/test_get_statistic.py::test_get_statistic_response_time -v` |
| TC-4.10 | Проверка заголовка Content-Type в ответе статистики | `pytest Task_2_1/tests/test_get_statistic.py::test_get_statistic_content_type_header -v` |
| TC-4.11 | Статистика при нулевых значениях всех полей | `pytest Task_2_1/tests/test_get_statistic.py::test_get_statistic_zero_values -v` |

---

## Линтер и форматтер

Проект настроен с использованием **flake8** (линтер), **black** (форматтер) и **isort** (сортировка импортов).

### Проверка кода линтером

```bash
flake8 tests/
```

---

## Allure-отчёт

### Генерация и открытие отчёта

```bash
# 1. Запустить тесты с сохранением результатов
pytest --alluredir=allure-results

# 2. Сгенерировать HTML-отчёт
allure generate allure-results -o allure-example --clean

# 3. Открыть отчёт в браузере
allure open allure-example
```

### Просмотр отчёта в реальном времени (Allure serve)

```bash
pytest --alluredir=allure-results
allure serve allure-results
```

---

## Описание библиотек

| Библиотека | Версия | Назначение |
|------------|--------|------------|
| `requests` | 2.32.3 | HTTP-клиент для выполнения API-запросов |
| `pytest` | 8.3.5 | Фреймворк для написания и запуска тестов |
| `allure-pytest` | 2.13.5 | Интеграция Allure с pytest для красивых отчётов |
| `pytest-html` | 4.1.1 | Генерация HTML-отчётов без Allure CLI |
| `flake8` | 7.1.1 | Статический анализатор кода (линтер) |
| `black` | 24.10.0 | Автоматический форматтер кода |
| `isort` | 5.13.2 | Сортировка и организация импортов |

---

