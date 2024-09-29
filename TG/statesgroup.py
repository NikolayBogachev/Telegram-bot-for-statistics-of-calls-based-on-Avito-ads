from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery


class AddTokenState(StatesGroup):
    waiting_for_token = State()
