import datetime

import peewee

import ezqr
import gls


class Client(gls.BaseModel):
    """ ... """

    chat_id = peewee.BigIntegerField(primary_key=True)
    """ Телеграм ID чата с пользователем """
    referral = peewee.ForeignKeyField('self', on_delete='SET NULL', null=True, default=None)
    """ Пользователь, по ссылке которого перешёл данный пользователь """
    season_points = peewee.IntegerField(default=0)
    """ Количество полученных пользователем бонусов в сезоне """
    terms_message_id = peewee.IntegerField(null=True, default=None)
    """ Телеграм ID сообщения, содержащего условия """
    created_at = peewee.DateTimeField()
    """ Дата регистрации пользователя """

    class Meta:
        table_name = 'Client'

    @classmethod
    def get_or_register(cls, user_id: int, referral: int = None, force_referral: bool = False) -> 'Client':
        """ Пытается получить пользователя из базы и, если не найден,
           добавить его. Реферал добавится только если у пользователя его нет """

        client, _ = cls.get_or_create(chat_id=user_id, defaults={
            'referral': referral,
            'created_at': datetime.datetime.now()
        })

        if force_referral and referral and not client.referral_id:
            client.referral = referral
            client.save()

        return client

    @classmethod
    def get_all_chats(cls) -> list[int]:
        return ezqr.fetch_values(' SELECT chat_id FROM "Client" ', {})
