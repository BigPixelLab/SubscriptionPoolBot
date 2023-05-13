# SubscriptionPoolBot

Bot to sell subscriptions

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
