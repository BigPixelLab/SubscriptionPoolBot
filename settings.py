import os

from apps.operator.settings import *
from apps.pool_bot.settings import *
from apps.search.settings import *

# BOT
BOT_TOKEN = os.environ['TOKEN']
DEBUG = True

# PAYMENTS
PAYMENTS_TOKEN = os.environ['PAYMENTS']
BILL_TIMEOUT_SEC = 900  # sec  (15 min)
QIWI_COMMISSION = 0.0204  # % / 100
QIWI_MIN_COMMISSION = 30  # rub
QIWI_PAY_METHODS = ['qw', 'card']

# DATABASE
DATABASE_URI = os.environ['DATABASE']

# MISC
FEEDBACK_TIME = 2  # sec
