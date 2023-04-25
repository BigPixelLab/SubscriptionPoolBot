""" ... """
import peewee

import gls


class ResourceCache(gls.BaseModel):
    """ ... """

    id = peewee.CharField()
    bot_id = peewee.BigIntegerField()
    file_id = peewee.TextField()
    is_fs = peewee.BooleanField()

    class Meta:
        primary_key = peewee.CompositeKey('bot_id', 'id')
        table_name = 'ResourceCache'
