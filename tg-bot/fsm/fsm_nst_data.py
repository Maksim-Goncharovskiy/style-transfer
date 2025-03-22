from aiogram.fsm.state import State, StatesGroup


class FsmNstData(StatesGroup):
    send_content = State()
    send_style = State()
    send_degree= State()
    wait_result = State()