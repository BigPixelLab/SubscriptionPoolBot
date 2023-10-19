from aiogram.filters.callback_data import CallbackData


class PostCallback(CallbackData, prefix="post"):
    reference_id: str


class LotteryOpenCallback(CallbackData, prefix='lottery-open'):
    prize_id: int
