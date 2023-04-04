""" ... """
from peewee import BigIntegerField, CharField, CompositeKey, TextField

import gls


class Resource(gls.BaseModel):
    """ ... """

    bot_id = BigIntegerField()
    path = CharField()
    file_id = TextField()

    # noinspection PyMissingOrEmptyDocstring
    class Meta:
        primary_key = CompositeKey('bot_id', 'path')
        table_name = 'Resource'
