from __future__ import annotations

from utils import database


def get_top_order_info() -> tuple[int, int] | None:
    """Returns order_id and customer"""
    return tuple(database.single_row(
        """
            select id, customer_id from "Order"
            where
                processed_by is null and
                closed_at is null
            order by created_at limit 1
        """,
        'Getting next order in a queue'
    ))
