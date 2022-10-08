from utils import database


def get_services_ordered_by_popularity():
    return database.fetch_values(
        """
            select E.name from "Service" E
            order by (
                select count(*) from "Order" O
                    join "Subscription" S on O.subscription = S.id
                where S.service = E.id
            ) desc
        """,
        'Getting services ordered by popularity'
    )


def get_support():
    return database.single_value(
        """
            select chat_id from "Support" limit 1
        """,
        'Getting support chat id'
    )
