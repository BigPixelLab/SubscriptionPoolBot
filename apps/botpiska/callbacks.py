import aiogram.filters.callback_data


class BuyButtonCallbackData(aiogram.filters.callback_data.CallbackData, prefix='buy'):
    """ ... """
    subscription_id: str


class GetForSelfButtonCallbackData(aiogram.filters.callback_data.CallbackData, prefix='get-for-self'):
    """ ... """
    pass


class GetAsGiftButtonCallbackData(aiogram.filters.callback_data.CallbackData, prefix='get-as-gift'):
    """ ... """
    pass
