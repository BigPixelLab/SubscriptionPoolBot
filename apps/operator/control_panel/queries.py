from . import models
from utils import database


def get_total_orders():
    return database.single_value(
        """ select count(*) from "Order" """,
        'Getting the number of orders'
    )


def get_top_open_orders(limit: int) -> list:
    return database.fetch_rows(
        """
            select
                O.id, O.created_at, O.processed_by, 
                E.name, 
                S.name, S.price 
            from "Order" as O
                join "Subscription" S on S.id = O.subscription
                join "Service" E on E.id = S.service
            where
                closed_at is null
            order by created_at
            limit %(limit)s
        """,
        'Getting open orders',
        limit=limit
    )
