import datetime

import settings
from utils import database
from . import models


def get_services() -> list[models.Service]:
    return database.fetch(
        models.Service,
        """ select * from "Service" """,
        'Getting list of services'
    )


def update_reserved_activation_codes():
    """Снимает резервацию с ключей для которых она истекла"""
    # Time when AC should've been reserved to expire now. Adding minute for extra safety
    time = datetime.datetime.now() - datetime.timedelta(seconds=settings.BILL_TIMEOUT_SEC + 60)
    database.execute(
        """
            update "ActivationCodes" AC set
                reserved_at = null,
                reserved_by = null
            where AC.reserved_at <= %(expired_time)s
        """,
        'Updating reserved activation codes',
        expired_time=time
    )


def get_sub_plans(service_id: int) -> list[models.Subscription]:
    return database.fetch(
        models.Subscription,
        """
            select * from "Subscription" S
            where
                S.service = %(service_id)s and (
                    -- No activation code is required
                    not S.is_code_required or 
                    
                    -- Activation code is required
                    S.is_code_required and (
                        -- Is there available activation codes for this subscription
                        select count(*) >= 1 from "ActivationCodes" AC
                        where 
                            AC.subscription = S.id and 
                            AC.linked_order is null and 
                            AC.reserved_at is null
                    )
                )
            order by S.type, S.duration
        """,
        f'Getting subscription plans for "{service_id=}"',
        service_id=service_id
    )
