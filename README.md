Python библиотека для работы с [business.ru API](http://developers.business.ru)
============================
### Установка
`pip install businessru-api`
### Примеры запросов к API
Далее отражено как выглядели бы описанные в [официальной документации](http://developers.business.ru/api-polnoe/primery_zaprosov_k_api/377)
примеры запросов при использовании ЯП Python с данным пакетом.
#### [Восстановление токена](http://developers.business.ru/api-polnoe/primery_zaprosov_k_api/377)
```python
from businessru_api import BusinessruAPI

client = BusinessruAPI(account, app_id, secret)
client.repair_token()
print(client.token)
```
Сразу же стоит отметить несколько отличий от официальной реализации на PHP:
- Немного изменены входные параметры
- На самом деле метод `client.repair_token` вызывается автоматически внутри `__init__`,
из-за чего нет смысла делать это самостоятельно при создании объекта
- Все взаимодействие с токеном инкапсулировано, и нет необходимости самостоятельно обновлять его значение
после каждого запроса, это делается тоже автоматически

#### [Отправка GET-запроса](http://developers.business.ru/api-polnoe/otpravka_get-zaprosa/384)
```python
from businessru_api import BusinessruAPI

client = BusinessruAPI(account, app_id, secret)

# запрашиваем интерактивную помощь по модели goods
response = client.request("get", "goods", help=1)
 
# либо запрашиваем полный список товаров и услуг
response = client.request("get", "goods")

# либо запрашиваем полный список товаров, отсортированный в порядке возрастания идентификатора
response = client.request("get", "goods", type=1,
                                          order_by="id")

# либо запрашиваем полный список товаров, отсортированный в порядке убывания идентификатора
response = client.request("get", "goods", **{'type': 1, 
                                             'order_by[id]': 'DESC'})
 
# либо запрашиваем полный список товаров и услуг с составной сортировкой 
response = client.request("get", "goods", **{'type': 1, 
                                             'order_by[partner_id]': 'ASC',
                                             'order_by[full_name]': 'ASC'})
 
# либо запрашиваем список услуг, помещенных в архив
response = client.request("get", "goods", archive=True, type=2)
 
# либо запрашиваем заказ покупателя c определенным идентификатором
response = client.request("get", "customerorders", id=123)
 
# либо запрашиваем заказы покупателя c заданными статусами 
response = client.request("get", "customerorders", status_id=[10, 21, 22, 23 ])
 
# либо запрашиваем заказы покупателя, дата создания которых находится в заданном диапазоне 
response = client.request("get", "customerorders", **{'date[from]': '01.12.2016',
                                                      'date[to]': '31.12.2016'})
 
# либо запрашиваем сделки, информация в которых была обновлена после заданного момента времени
response = client.request("get", "deals", **{'updated[from]': '01.12.2016 12:00:00'})

# извлекаем данные
print(response['result'])
```
Главное отличие заключается в том, что вам не нужно самостоятельно проверять статус результата, поскольку если что-то пойдет не так,
то вызовется Exception.

#### [Обработка POST-запроса](http://developers.business.ru/api-polnoe/otpravka_post-zaprosa/385)
```python
from businessru_api import BusinessruAPI

client = BusinessruAPI(account, app_id, secret)

# создаем товар с наименованием “Мороженое”
response = client.request("post", "goods", name="Мороженое")

print(response['result'])
```

#### [Обработка заказов покупателей](http://developers.business.ru/api-polnoe/obrabotka_zakazov_pokupatelej/386)
```python
from datetime import datetime
from itertools import count

from businessru_api import BusinessruAPI


secret = "Hgl6Q1GF8lwHZbRX3nq7fO8MEytNsdJ0";
app_id = "461979";
account = 'myaccount';
client = BusinessruAPI(account, app_id, secret)
method = 'get';
model = 'offers';
date_to_compare_with = datetime.now()
for page in count(1):
    result = client.request(method, model, limit=250, page=page)
    if not result:
        # заказов больше нет
        break
    for item in result:
        # отбираем заказы, обновленные позднее заданной метки времени
        updated = datetime.strptime(item['updated'], "%d.%m.%Y %H:%M:%S.%f")
        if updated > date_to_compare_with: 
            # выполняем необходимые действия с отобранными заказами  
            pass
```

#### [Работа с дополнительными полями](http://developers.business.ru/api-polnoe/rabota_s_dopolnitelnymi_polyami/387)
```python
from businessru_api import BusinessruAPI


secret = "Hgl6Q1GF8lwHZbRX3nq7fO8MEytNsdJ0"
app_id = "461979"
account = 'myaccount'
client = BusinessruAPI(account, app_id, secret)


# Считываем данные модели partners с дополнительными полями
method = 'get'
model = 'partners'
res = client.request(method, model, with_additional_fields=1)


# добавляем контрагента, инициализируем доп. поле 23698467 значением "Особо ценный контрагент"
# подразумевается что доп. поле имеет тип Техт
method  = 'post'
params = {
    'name': 'Контрагент1',
    '23698467': 'Особо ценный контрагент'
}
res = client.request(method, model, **params)


# редактируем доп. поле контрагента
method  = 'put'
params = {
    'id': '23693351',
    '23698467': 'Просто ценный контрагент'
}
res = client.request(method, model, **params)
```
### Несколько заметок
- `BusinessruAPI` методы `request`, `get`, `post` и `put` делают от `1` до `BusinessruAPI.max_retry` запросов в зависимости от того,
когда вернется успешный ответ или вызовется исключение, отличное от `TooManyRequests` и `InvalidToken`. Дефолтное значение 
`BusinessruAPI.max_retry` равно `10` и является последним аргументом `BusinessruAPI.__init__`.
- `BusinessruAPI` кроме метода `request` содержит так же методы `get`, `post` и `put` позволяющие писать немного короче:
    - `client.request('get', model, **params)` -> `client.get(model, **params)`
    - `client.request('post', model, **params)` -> `client.post(model, **params)`
    - `client.request('put', model, **params)` -> `client.put(model, **params)`
- При работе с [business.ru API](http://developers.business.ru) я столкнулся с ответами, статус коды которых незадокументировны. 
Изучив запросы на которые приходят данные ответы, было решено интерпретировать их следующим образом:
    - __405__ -- несуществующий эндпоинт, `EndpointNotFound`
    - __504__ -- количество запросов на единицу времени превышено, `TooManyRequests`
