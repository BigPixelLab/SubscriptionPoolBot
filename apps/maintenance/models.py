""" ... """
import peewee

import gls


class ResourceCache(gls.BaseModel):
    """ ... """

    path = peewee.CharField()
    bot_id = peewee.BigIntegerField()
    file_id = peewee.TextField()

    class Meta:
        primary_key = peewee.CompositeKey('bot_id', 'path')
        table_name = 'ResourceCache'
