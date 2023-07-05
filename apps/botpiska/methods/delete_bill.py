import contextlib

import aiogram
import peewee
from glQiwiApi.qiwi.exceptions import QiwiAPIError

import gls
import response_system as rs
from apps.botpiska.models import Bill
from utils import do_nothing


class BillIsPaid(rs.UserFriendlyException):
    """ Счёт, который пытаются удалить, оплачен """


async def delete_bill(user: aiogram.types.User) -> rs.Response:
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
        return rs.no_response()

    # noinspection PyUnusedLocal
    qiwi_bill = None

    with contextlib.suppress(QiwiAPIError):
        qiwi_bill = await gls.qiwi.get_bill_by_id(bill.qiwi_id)

    if qiwi_bill is not None:

        # Имеется счёт и он оплачен, в этой ситуации удаление
        # сообщения или счёта приведут к потере денег пользователем.
        # Скамить не хочется
        if qiwi_bill.status.value == 'PAID':
            raise BillIsPaid(
                'У вас имеется не закрытый оплаченный счёт. '
                'Чтобы сгенерировать новый, сначала завершите '
                'предыдущий заказ'
            )

        # В противном случае можно отозвать счёт, чтобы его больше
        # нельзя было оплатить
        with contextlib.suppress(QiwiAPIError):
            await gls.qiwi.reject_p2p_bill(qiwi_bill.id)

    bill.delete_instance()
    return rs.delete(bill.message_id, on_error=do_nothing)


__all__ = ('delete_bill',)
