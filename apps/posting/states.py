from aiogram.fsm.state import StatesGroup, State


class PostStates(StatesGroup):
    WAITING_FOR_POST = State()
