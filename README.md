**Pamm Service**

**Доступные REST API методы:**

1. **POST**  `<domain>/<category>/accounts/get`
Метод отдает памм счета.

2. **POST**  `<domain>/<category>/accounts/status/get`
Метод отдает памм счета с их статусами.

3. **POST**  `<domain>/<category>/investors/get`
Метод отдает инвесторов.
Имеет дополнительные фильтры:
    - `account_id` - Идентификатор - Запрос записей по указанному ID памм счета - **INTEGER**


4. **POST**  `<domain>/<category>/orders/get`
Метод отдает ордера (транзакции), те что хранит в себе сервис.
Имеет дополнительные фильтры:
    - `account_id` - Идентификатор - Запрос записей по указанному ID памм счета - **INTEGER**
    - `order_status_id` - Идентификатор - Запрос записей по указанному статус ID ордера - **INTEGER**
       - 1 - **NEW**
       - 2 - **PROCESS**
       - 3 - **DONE**
       - 4 - **DECLINE**
       - 5 - **FAIL**

5. **POST**  `<domain>/<category>/early-rollover/set`
Метод задает досрочный (или промежуточный) ролловер. 
Имеет аттрибуты:
    - `account_id` - Идентификатор - ID памм счета - **INTEGER** (**REQUIRED**)
    - `timestamp` - DATETIME - Дата и время когда будет совершен досрочный ролловер. Если не указывать, будет взято ближайшее. - **INTEGER** (**NOT REQUIRED**)


**Пример:**

**POST**  `api.example.com/pamm/accounts/status/get`

**Body:**
```
{}
```
**Response:**
```
[
  {
    "id": 87813,
    "user_id": 2,
    "params": {
      "min_invest": "1000",
      "reward_percent": "50",
      "rollover_period": "172800",
      "pub_stat_lag": "7200",
      "started_at": "1575559800"
    },
    "currency": {
      "digits": 2,
      "id": 1
    },
    "created_at": 1575558974,
    "activated_at": 1575559800,
    "start_at": 1575732600,
    "stop_at": 1575905400,
    "status_code_id": 2
  },
  ...
]
```

**Информация**
1. В теле любого запроса ВСЕГДА должен передаваться **JSON**. Даже если он пустой.
2. Ответ приходит ВСЕГДА в формате **JSON**.
3. **API** имеет валидацию, а так же человеку-понятные сообщения в случае ошибки в запросе.
4. На данный момент все методы **API** с приставкой `/get` имеют стандартный набор фильтров:
    - `from` - ОТ - Запрос записей от указанного ID - **INTEGER**
    - `to` - ДО - Запрос записей до указанного ID - **INTEGER**
    - `id` - Идентификатор - Запрос записи по указанному ID - **INTEGER**
    - `ids` - Идентификаторы - Запрос записей по указанным ID - **JSON ARRAY**
    Например:
      `"ids": [1001, 1002, 1003]`
    - `offset` - Отступ - Запрос записей с начальным отступом по ID - **INTEGER**
    - `limit` - Лимит - Запрос записей с указанным лимитом на их количество - **INTEGER**
 Все фильтры необходимо поместить во вложенный **JSON** объект `filters`.
 Таким образом должно получиться такое тело запроса:
 ```
{
  "filters": {
    "from": 1000,
    "to": 2000
  }
}
 ```

**Особенности**
 - Все фильтры совместимы и не обязательны
 - **API** имеет по умолчанию лимит на количество записей в одном запросе - 1000 (настраиваемо)
 - Все временные метки указаны в **UTC**
 - Поле `status_code_id` указывает на состояние счета:
   - 1 - **NEW**
   - 2 - **TRADING**
   - 3 - **ROLLOVER**
   - 4 - **CLOSED**
   - 5 - **DENIED** | **REJECTED**

**Дополнительная информация:**

Все денежные атрибуты (`amount`) имеют **INTEGER** представление, кроме информативных строковых. И хранятся в их минимальных величинах. Например для доллара - это будет центы, для Коинов - сатоши и тд. Их необходимо форматировать в соответствии с данными о валюте. Функция форматирования **INTEGER** в **STRING** на языке **JS** может выглядеть вот так:
```
function itos(n, d)
{
  return (n * Math.pow(10, -d)).toFixed(d)
}
```
Где `n`- number - целое конвертируемое число, `d` - digits - количество знаков после запятой.