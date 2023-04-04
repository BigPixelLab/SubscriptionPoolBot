# SubscriptionPoolBot

Bot to sell subscriptions

### ADD NEW RESOURCE

Чтобы добавить новый ресурс, необходимо, во-первых - 
создать колонку в базе данных DEV и RELEASE с типом
text, во-вторых - в файле `resources/__init__.py` в
список `RESOURCES` добавить новый ресурс, после чего
запустить бота и вызвать команду `/updrs <resource_index>`
с переданным индексом только что созданного ресурса.

### GET PROJECT STATISTICS

Чтобы посмотреть статистику проекта, такую как количество
строк или файлов, введи в командной строке:

`./cloc.exe $(git ls-files)`

### GET CURRENT TIME IN HANDLERS

Чтобы получить текущее время, в handler-ах, вместо
`datetime.datetime.now()` необходимо использовать
`response_system.global_time.get()`. Таким образом
возвращается время, установленное в момент начала
обработки handler-а и оно будет одинаковым везде в
пределах этого handler-а
