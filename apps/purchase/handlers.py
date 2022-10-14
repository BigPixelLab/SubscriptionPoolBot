import datetime
import decimal
import logging
from pathlib import Path

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, WebAppInfo
from glQiwiApi.qiwi.exceptions import QiwiAPIError

import gls
import settings
from utils import template
from utils.input_file_types import BufferedInputFile
from ..search import models as search_models
from ..orders import models as order_models
from ..coupons import models as coupon_models
from . import callbacks, image_generation, models

TEMPLATES = Path('apps/purchase/templates')
logger = logging.getLogger(__name__)


async def buy_handler(query: CallbackQuery, callback_data: callbacks.BuySubscriptionCallback, state: FSMContext):
    subscription = search_models.Subscription.get(callback_data.sub_id)

    # queries.is_user_have_reserved_ac(query.from_user.id, callback_data.sub_id)
    if subscription.is_code_required and models.ActivationCode.is_reserved(query.from_user.id, callback_data.sub_id):
        # PLAN: Продлевать резервацию
        await query.answer('Вы уже недавно пытались купить эту подписку, поищите счёт '
                           'или подождите пока он истечёт и попробуйте снова')
        return

    # Reserving activation code if needed, if reservation fails, body is executed
    if subscription.is_code_required and not models.ActivationCode.reserve(query.from_user.id, callback_data.sub_id):
        await query.answer('Кажется кто-то успел купить последнюю такую подписку пока вы выбирали, но ничего '
                           'другие варианты всё ещё могут быть доступны, а мы пока завезём побольше этих')
        return

    total_price = subscription.price

    # Coupon stuff
    data = await state.get_data()

    if coupon_code := data.get('coupon'):
        coupon = coupon_models.Coupon.get_free(coupon_code)
        coupon_discount = round(total_price * decimal.Decimal(coupon.discount / 100), 2)
        total_price -= coupon_discount
    else:
        coupon = None
        coupon_discount = 0

    # Taking into account qiwi commission.
    # >> init_price + init_price * commission = final_price
    # We want our final_price to be price of the subscription
    # plus coupon aka total_price. So, solving for init_price, we get:
    # >> init_price = final_price / (1 + commission)
    total_price *= 1 / (1 + settings.QIWI_COMMISSION)

    service = subscription.get_service()

    expire_date = datetime.datetime.now() + datetime.timedelta(seconds=settings.BILL_TIMEOUT_SEC)
    async with gls.qiwi:
        try:
            bill = await gls.qiwi.create_p2p_bill(
                amount=round(total_price, 2),
                pay_source_filter=['qw', 'card'],
                expire_at=expire_date
            )
        except QiwiAPIError as error:
            await query.answer('Что-то не так с qiwi api, пожалуйста, обратитесь в поддержку')
            logger.error(error)
            return

    render = template.render(TEMPLATES / 'bill.xml', {
        'buy_button': {'web_app': WebAppInfo(url=bill.pay_url)},
        'pay_url': bill.pay_url,
        'subscription': subscription,
        'service': service,
        'failed': False,
    })

    message = render.first()
    message.photo = BufferedInputFile(
        image_generation.render_bill(
            total=total_price,
            subscription=subscription,
            service=service,
            coupon=coupon,
            coupon_discount=coupon_discount
        ),
        'bill.png'
    )
    await message.send(query.message.chat.id)
    await query.answer()
