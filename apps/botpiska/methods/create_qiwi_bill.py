import asyncio
import datetime
import logging

import aiohttp.client_exceptions
import glQiwiApi
import glQiwiApi.qiwi.exceptions
import glQiwiApi.qiwi.clients.p2p.types as qiwi_types

import settings
from result import *

logger = logging.getLogger(__name__)


async def create_qiwi_bill(
        client: glQiwiApi.QiwiP2PClient,
        amount: str,
        expires: datetime.datetime
) -> Result[qiwi_types.Bill, None]:
    """ ... """

    while True:
        try:
            return Ok(await client.create_p2p_bill(
                amount=amount,
                pay_source_filter=settings.QIWI_PAY_METHODS,
                expire_at=expires
            ))
        except glQiwiApi.qiwi.exceptions.QiwiAPIError:
            return Error()
        except aiohttp.client_exceptions.ClientConnectorError as error:
            logger.info(error)
            await asyncio.sleep(0.2)
            continue
