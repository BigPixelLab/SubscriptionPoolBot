import contextlib

import aiogram
import peewee
from glQiwiApi.qiwi.exceptions import QiwiAPIError

import gls
import response_system as rs
import response_system.core.middleware
import response_system.core.responses
from apps.botpiska.models import Bill
from result import *


async def delete_previous_bill(user: aiogram.types.User) -> Result[None, str]:
    """
       Проверяет наличие ранее сгенерированного счёта и, если он не оплачен,
       удаляет его из базы и соответствующее ему сообщение из чата.
       Сообщение со счётом удаляется моментально, т.е. не через Response

       Возможные ошибки:
         - BILL_IS_PAID - Прошлый счёт был оплачен, но не закрыт
    """

    try:
        bill = Bill.get_by_id(user.id)
    except peewee.DoesNotExist:  # Нет ранее сгенерированного счёта, так что всё норм
        return Ok()

    # noinspection PyUnusedLocal
    qiwi_bill = None

    with contextlib.suppress(QiwiAPIError):
        qiwi_bill = await gls.qiwi.get_bill_by_id(bill.qiwi_id)

    if qiwi_bill is not None:

        # Имеется счёт и он оплачен, в этой ситуации удаление
        # сообщения или счёта приведут к потере денег пользователем.
        # Скамить не хочется
        if qiwi_bill.status.value == 'PAID':
            return Error('BILL_IS_PAID')

        # В противном случае можно отозвать счёт, чтобы его больше
        # нельзя было оплатить
        with contextlib.suppress(QiwiAPIError):
            await gls.qiwi.reject_p2p_bill(qiwi_bill.id)

    bill.delete_instance()
    rs.respond(rs.delete(bill.message_id))

    return Ok()


__all__ = ('delete_previous_bill',)
