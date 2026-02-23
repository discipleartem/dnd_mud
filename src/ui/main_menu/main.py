from .new_game import new_game
from .load_game import load_game
from .settings import settings
from i18n import t

# Получаем список пунктов меню
MAIN_MENU = t('menu.items')
     


def show_main_menu() -> None:
    """Показать главное меню."""
    while True:
        # Очистка экрана и вывод заголовка
        print("\n" + "="*40)
        print(t('menu.title').center(40))
        print("="*40)
        
        # Вывод пунктов меню с нумерацией
        for i, item in enumerate(MAIN_MENU, 1):
            print(f"{i}. {item}")
        
        print("="*40)
        
        # Получение и валидация выбора пользователя
        choice = input(t('menu.prompt')).strip()
        
        # Валидация ввода
        if not choice.isdigit():
            print(t('menu.errors.invalid_number'))
            input(t('main.welcome.press_enter'))
            continue
            
        choice_num = int(choice)
        
        if choice_num < 1 or choice_num > len(MAIN_MENU):
            print(t('menu.errors.out_of_range', max=len(MAIN_MENU)))
            input(t('main.welcome.press_enter'))
            continue
        
        # Обработка выбора
        if choice_num == 1:
            new_game()
        elif choice_num == 2:
            load_game()
        elif choice_num == 3:
            settings()
        elif choice_num == 4:
            print(t('menu.goodbye'))
            break
            
        # После возврата из подменю - пауза перед показом главного меню
        if choice_num != 4:
            input(t('menu.continue'))
