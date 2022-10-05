from . import models
from utils import database


def get_total_orders():
    return database.single_value("""
        select count(*) from "Order"
    """)


def get_top_open_orders(limit: int) -> list[models.OrderInfo]:
    results = database.fetch_rows("""
        select
            O.id, 
            O.created_at, 
            O.processed_by is not null, 
            E.name, 
            S.name, 
            S.price 
        from "Order" as O
            join "Subscription" S on S.id = O.subscription
            join "Service" E on E.id = S.service
        where
            closed_at is null
        order by created_at
        limit %s
    """, limit)
    return [models.OrderInfo(*result) for result in results]

