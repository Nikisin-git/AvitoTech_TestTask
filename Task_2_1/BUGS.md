# Баг-репорты: API сервиса объявлений Avito QA Internship 2026

**Хост:** `https://qa-internship.avito.com`  
**Дата тестирования:** Апрель 2026  
**Окружение:** Python 3.11, pytest 8.3.5, requests 2.32.3, ОС: Windows 11 / macOS 14 / Ubuntu 22.04  

## BUG-001: Создание объявления без поля statistics - сервер возвращает 400
### Краткое описание
API не допускает случаев, если объявление создается без параметров statistics. Вместо кода 200, сервер возвращает 400. Хотя в документации данное поле было помечено как необязательное. 

### Шаги воспроизведения:
1. Отправить POST /api/1/item без поля statistics:
```json
{
  "sellerID": 1,
  "name": "Объявление без статистики",
  "price": 500
}
```
2. Проверить HTTP-код ответа.
3. Проверить наличие поля `id` в ответе.

### Фактический результат
- HTTP-статус: **400**.
- Не допускается создание объявление без `statistics`.

#### Ожидаемый результат:
- HTTP-статус: **200 OK**.
- Тело ответа содержит поле `id`.
- Поле `statistics` либо отсутствует, либо содержит дефолтные нулевые значения.

Скриншот:

![](https://github.com/Nikisin-git/AvitoTech_TestTask/blob/main/Task_2_1/bugreport_images/Screen%201.1.png)





![](https://github.com/Nikisin-git/AvitoTech_TestTask/blob/main/Task_2_1/bugreport_images/Screen%201.2.png)

---

## BUG-002: Недопустимость создания объявления с нулевой ценой

### Краткое описание:
API не принимает объявления с нулевым значением поля "price" и возвращает ответ "400 Bad request". Нулевая цена семантически допустима, но сервер воспринимает нулевую цену как отсутствие поля вовсе.

### Шаги воспроизведения:
1. Выполнить POST-запрос на `POST /api/1/item` с телом:

```json
{
  "sellerID": 1,
  "name": "Бесплатное объявление",
  "price": 0,
  "statistics": { "likes": 0, "viewCount": 0, "contacts": 0 }
}
```
2. Проверить HTTP-код ответа.
3. Проверить значение поля `price` в ответе.

#### Ожидаемый результат:
- HTTP-статус: **200 OK**.
- Поле `price` в ответе равно `0`.

### Фактический результат
- HTTP-статус: **400 Bad Request**
- Объявление не создается
- Нулевая цена воспринимается как отсутствие цены

Скриншоты:

![](https://github.com/Nikisin-git/AvitoTech_TestTask/blob/main/Task_2_1/bugreport_images/Screen%202.1.png)



![](https://github.com/Nikisin-git/AvitoTech_TestTask/blob/main/Task_2_1/bugreport_images/Screen%202.2.png)

---

## BUG-003: Недопустимость создания объявления с нулевыми параметрами статистики

### Краткое описание:
API не допускает случаев, если объявление создается с параметрами statistics, но равными нулю. Хотя при создании объявление не должно иметь никаких просмотров и избранных. Вместо ответа 200, возвращается ответ "400 Bad Request". 

### Шаги воспроизведения:
1. Выполнить POST-запрос на `POST /api/1/item` с телом:
```json
{
  "sellerID": get_unique_seller_id(),
  "name": "Нулевая статистика",
  "price": 200,
  "statistics": { "likes": 0, "viewCount": 0, "contacts": 0 }
}
```
2. Проверить HTTP-код ответа и значения полей статистики в ответе.


### Фактический результат
- HTTP-статус: **400 Bad Request**.
- Не допускается создание объявление с нулевыми параметрами `statistics`.
- Возврашается сообщение "поле likes (viewCount или contacts) обязательно".
- Нулевые параметры воспринимаются как их отсутствие.

#### Ожидаемый результат:
- HTTP-статус: **200 OK**.
- Поля `likes`, `viewCount`, `contacts` в ответе равны `0`.

Скриншоты:

![](https://github.com/Nikisin-git/AvitoTech_TestTask/blob/main/Task_2_1/bugreport_images/Screen%203.1.png)


![](https://github.com/Nikisin-git/AvitoTech_TestTask/blob/main/Task_2_1/bugreport_images/Screen%203.2.png)

---

## BUG-004: Создание объявления с отрицательной ценой — сервер возвращает 200 OK вместо 400

### Краткое описание
API принимает объявления с отрицательным значением поля `price` и возвращает статус `200 OK` вместо ошибки валидации `400 Bad Request`. Отрицательная цена является логически некорректной для объявления о продаже.

### Шаги воспроизведения:
1. Отправить POST-запрос на `https://qa-internship.avito.com/api/1/item` с телом:
```json
{
  "sellerID": 1,
  "name": "Объявление с отрицательной ценой",
  "price": 500,
  "statistics": { "likes": 1, "viewCount": 1, "contacts": 1 }
}
```
2. Убедиться в наличии заголовков `Content-Type: application/json` и `Accept: application/json`.
3. Получить и проанализировать ответ сервера.

### Фактический результат
- HTTP-статус: **200 OK**
- Объявление создаётся с `price = -500`

### Ожидаемый результат
- HTTP-статус: **400 Bad Request**
- Тело ответа содержит сообщение об ошибке валидации, например:
```json
{
  "result": {
    "message": "price must be non-negative"
  },
  "status": "error"
}
```
Скриншоты:

![](https://github.com/Nikisin-git/AvitoTech_TestTask/blob/main/Task_2_1/bugreport_images/Screen%204.1.png)


![](https://github.com/Nikisin-git/AvitoTech_TestTask/blob/main/Task_2_1/bugreport_images/Screen%204.2.png)

---

## BUG-005: Создание объявления с sellerID вне допустимого диапазона (слишком большой integer)

### Краткое описание
API принимает объявления с очень большим значением sellerID и возвращает статус `200 OK` вместо ошибки валидации `400 Bad Request`. Хотя в задании было сказано, что допускается генерировать sellerId только в диапазоне 111111–999999. Выход за пределы диапазона является некорректным.

### Шаги воспроизведения:
1. Выполнить POST-запрос на `POST /api/1/item` с телом:
```json
{
  "sellerID": 9999999999,
  "name": "Огромный sellerID",
  "price": 100,
  "statistics": { "likes": 1, "viewCount": 1, "contacts": 1 }
}
```
2. Проверить HTTP-код ответа.

#### Ожидаемый результат:
- HTTP-статус: **400 Bad Request**.

### Фактический результат
- HTTP-статус: **200 OK**
- Объявление создаётся большим значением SellerID

Скриншоты:

![](https://github.com/Nikisin-git/AvitoTech_TestTask/blob/main/Task_2_1/bugreport_images/Screen%205.1.png)


![](https://github.com/Nikisin-git/AvitoTech_TestTask/blob/main/Task_2_1/bugreport_images/Screen%205.2.png)


---
## BUG-006: Допустимость создания объявления с отрицательным sellerID

### Краткое описание
API принимает объявления с отрицательным значением поля `SellerID` и возвращает статус `200 OK` вместо ошибки валидации `400 Bad Request`. Отрицательный `SellerID`  является недопустимым для объявления о продаже.

### Шаги воспроизведения:
1. Выполнить POST-запрос на `POST /api/1/item` с телом:
```json
{
  "sellerID": -111111,
  "name": "Отрицательный sellerID",
  "price": 100,
  "statistics": { "likes": 1, "viewCount": 1, "contacts": 1 }
}
```
2. Проверить HTTP-код ответа.


### Фактический результат
- HTTP-статус: **200 OK**
- При вводе `SellerID =-111111` появляется сообщение об успешном сохранении объявления

### Ожидаемый результат
- HTTP-статус: **400 Bad Request**
- Тело ответа содержит сообщение об ошибке валидации, например:
```json
{
  "result": {
    "message": "SellerID be non-negative"
  },
  "status": "error"
}
```
Скриншоты:

![](https://github.com/Nikisin-git/AvitoTech_TestTask/blob/main/Task_2_1/bugreport_images/Screen%206.1.png)


![](https://github.com/Nikisin-git/AvitoTech_TestTask/blob/main/Task_2_1/bugreport_images/Screen%206.2.png)

---

### BUG-007: Получение объявлений с отрицательным sellerID

### Краткое описание
API успешно принимает отрицательные значения `SellerID`. API успешно обрабатывает запрос со статусом "200 ОК" и предоставляет информацию об объявлении. Хотя отрицательный `SellerID`  является недопустимым для объявления о продаже.  

### Шаги воспроизведения:
1. Выполнить GET-запрос на `GET /api/1/-111111/item`.
2. Проверить HTTP-код ответа.

#### Ожидаемый результат:
- HTTP-статус: **400 Bad Request**.

### Фактический результат
- HTTP-статус: **200 OK**
- По отрицательному `SellerID` пользователь успешно получает информацию об объявлении 

Скриншоты:

![](https://github.com/Nikisin-git/AvitoTech_TestTask/blob/main/Task_2_1/bugreport_images/Screen%207.1.png)


![](https://github.com/Nikisin-git/AvitoTech_TestTask/blob/main/Task_2_1/bugreport_images/Screen%207.2.png)


---

### BUG-008: Получение объявлений с нулевым sellerID

### Краткое описание
API принимает объявления с нулевым `sellerID` и возвращает `200 OK`. Идентификатор продавца не должен быть отрицательным числом.

### Шаги воспроизведения:
1. Выполнить GET-запрос на `GET /api/1/0/item`.
2. Проверить HTTP-код ответа.

#### Фактический результат:
- HTTP-статус: **200 OK**
- По нулевом `SellerID` пользователь получает пустую информацию 

#### Ожидаемый результат:
- HTTP-статус: **400 Bad Request** или **404 Not Found**.

Скриншоты:

![](https://github.com/Nikisin-git/AvitoTech_TestTask/blob/main/Task_2_1/bugreport_images/Screen%208.1.png)


![](https://github.com/Nikisin-git/AvitoTech_TestTask/blob/main/Task_2_1/bugreport_images/Screen%208.2.png)

### BUG-009: Получение объявлений с очень большим sellerID

### Краткое описание
API принимает объявления с очень больщим `sellerID`, превышающим допустимый диапазон, и возвращает `200 OK`. При этом в задании было сказано, что допускается генерировать sellerId только в диапазоне 111111–999999. Выход за пределы диапазона является некорректным.

---

#### Шаги воспроизведения:
1. Выполнить GET-запрос на `GET /api/1/9999999999/item`.
2. Проверить HTTP-код ответа.

#### Фактический результат:
- HTTP-статус: **200 OK**
- По `SellerID` пользователь получает информацию о ранее созданном объявлении с большим `SellerID.

#### Ожидаемый результат:
- HTTP-статус: **400 Bad Request** или **404 Not Found**.

Скриншоты:

![](https://github.com/Nikisin-git/AvitoTech_TestTask/blob/main/Task_2_1/bugreport_images/Screen%209.1.png)


![](https://github.com/Nikisin-git/AvitoTech_TestTask/blob/main/Task_2_1/bugreport_images/Screen%209.2.png)

---

### BUG-010: Не возвращается статистика при нулевых значениях всех полей

### Краткое описание
Невозможно получить информацию об объявлении с нулевыми параметрами статистики. Это связано и с тем, что API POST /api/1/item тоже не отрабатывает должным образом. Это противоречит логике, поскольку изначально объявление должно создаваться без избранных и просмотров.

#### Предусловия:
1. Создать объявление с `statistics: { likes: 0, viewCount: 0, contacts: 0 }`.

### Шаги воспроизведения:
1. Запросить статистику для данного объявления.
2. Проверить значения полей.

#### Фактический результат:
- HTTP-статус: **400 Bad Request** или **404 Not Found**.

#### Ожидаемый результат:
- Поля `likes`, `viewCount`, `contacts` равны `0`.



