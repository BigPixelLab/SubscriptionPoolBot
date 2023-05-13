import peewee

import gls


class SubscriptionGroup(gls.BaseModel):
    """ ... """

    id = peewee.CharField(primary_key=True)
    parent = peewee.ForeignKeyField('self', on_delete='CASCADE', null=True)
    subscription = peewee.DeferredForeignKey('Subscription', on_delete='CASCADE', null=True)

    class Meta:
        table_name = 'SubscriptionGroup'
