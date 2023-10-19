import datetime
import functools
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

    def award_points(self, points: int):
        """ Начисление бонусов пользователю и тому кто его пригласил """
        self.season_points += points
        self.save()

        referral = self.referral
        if referral is None:
            return

        referral.season_points += points
        referral.save()

    @functools.cached_property
    def rating_position(self):
        """ Возвращает позицию пользователя в рейтинге, исходя из набранного им кол-ва очков """
        query = """
            SELECT COUNT(*) + 1 
            FROM (
                SELECT season_points
                FROM "Client"
                ORDER BY season_points DESC
            ) AS scores
            WHERE scores.season_points > %(season_points)s
        """
        return ezqr.single_value(query, {'season_points': self.season_points})

    @functools.cached_property
    def clients_invited(self):
        """ Возвращает кол-во пользователей, которые были приглашены по реф-ссылке  """
        query = """
            SELECT COUNT(*) 
            FROM "Client"
            WHERE referral_id = %(chat_id)s;
        """
        return ezqr.single_value(query, {'chat_id': self.chat_id})

    @classmethod
    def get_or_register(cls, user_id: int, referral: int = None, force_referral: bool = False) -> tuple['Client', bool]:
        """ Пытается получить пользователя из базы и, если не найден,
           добавить его. Реферал добавится только если у пользователя его нет """

        client, is_created = cls.get_or_create(chat_id=user_id, defaults={
            'referral': referral,
            'created_at': datetime.datetime.now()
        })

        if force_referral and referral and not client.referral_id:
            client.referral = referral
            client.save()

        if is_created:
            ezqr.execute("""
                INSERT INTO "Statistics" (client_id, action_id, data, created_at)
                VALUES (%(client_id)s, 'registration', '{}', now())
            """, {'client_id': user_id})

        return client, is_created

    @classmethod
    def get_all_chats(cls) -> list[int]:
        """ ... """
        return ezqr.fetch_values(' SELECT chat_id FROM "Client" ', {})
