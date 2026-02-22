from typing import Dict, Callable

from ..user_choice import get_user_choice
from .new_game import new_game
from .load_game import load_game
from .settings import settings


MAIN_MENU = {
    "Новая игра": new_game,
    "Загрузить игру": load_game,
    "Настройки": settings
}


def show_main_menu() -> None:
    """Показать главное меню."""
    get_user_choice(
        title="Выберите действие",
        items=MAIN_MENU,
        exit_item={"Выход": exit}
    )

