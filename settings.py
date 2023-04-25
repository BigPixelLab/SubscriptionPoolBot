import datetime
import decimal
import logging
import string
import os


# BOT -----------------------------------------------------

# Токены с которыми будут запущены основной бот и бот оператора.
# Можно получить в BotFather
BOT_TOKEN = os.environ['TOKEN']
OPERATOR_BOT_TOKEN = os.environ['OPERATOR_TOKEN']

# Включает/выключает режим разработки. Некоторые функции бота
# будут доступны исключительно в этом режиме
DEBUG = 'DEBUG' in os.environ

# Пути к библиотекам внутри проекта. Все указанные пути просто
# будут добавлены в sys.path
# Должны быть указаны директории!
LIBS = [
    'libs'
]


# CONTACTING ----------------------------------------------

# Telegram ID пользователя, являющегося оператором поддержки
SUPPORT_CHAT_ID = 839882467

# Telegram ID пользователя, являющегося оператором тех. поддержки
TECH_SUPPORT_CHAT_ID = 1099569178


# PAYMENTS ------------------------------------------------

# Токен p2p переводов в qiwi
PAYMENTS_TOKEN = os.environ['PAYMENTS']

# Время, через которое счёт станет недействительным.
# Произвольное значение
BILL_TIMEOUT = datetime.timedelta(minutes=15)  # sec  (15 min)

# Комиссия qiwi за перевод
QIWI_COMMISSION = decimal.Decimal(0.0204)  # % / 100

# Методы оплаты, доступны: qw, card, mobile
# Порядок не важен
QIWI_PAY_METHODS = ['qw', 'card']


# COUPONS -------------------------------------------------

# Символы, использующиеся для генерации купонов
COUPON_ALLOWED_SYMBOLS = string.ascii_uppercase + string.digits + '-'

# Время, которое купон купленный в подарок будет действителен
# с момента покупки
GIFT_COUPON_VALID_INTERVAL = datetime.timedelta(days=365)

# Время, которое купон полученный по акции 1+1 будет действителен
# с момента получения
EVENT_1P1_COUPON_VALID_INTERVAL = datetime.timedelta(days=30)


# DATABASE ------------------------------------------------

# URL базы данных, формируется как
# postgres://{USER}:{PASSWORD}@localhost:{PORT}/{DATABASE}
DATABASE_URI = os.environ['DATABASE_URL']


# LOGGING -------------------------------------------------

# Уровень логирования, все сообщения с меньшим уровнем будут игнорироваться
LOGGING_LEVEL = logging.INFO

# Формат логов
LOGGING_FORMAT = '%(filename)s:%(lineno)d #%(levelname)-8s ' \
                 '[%(asctime)s] - %(name)s - %(message)s'


# OUTPUT --------------------------------------------------

# Формат по умолчанию для вывода сообщений.
# Если используется шаблонизатор (а он используется)
# лучше оставить HTML
DEFAULT_PARSE_MODE = 'HTML'  # See telegram api docs for more...


# MISC ----------------------------------------------------

# Размеры текстовых полей для разных целей в базе данных
COUPON_MAX_LENGTH = 6

# За сколько дней заранее нужно оповестить пользователя,
# что его подписка заканчивается
NOTIFY_BEFORE = datetime.timedelta(days=3)  # 3
