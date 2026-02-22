from typing import Dict, Callable, Optional


def validate_choice(choice: str, max_value: int) -> int:
    """Проверяет корректность выбора пользователя."""
    try:
        choice_num = int(choice)
        if 1 <= choice_num <= max_value:
            return choice_num
        raise ValueError(f"Число должно быть от 1 до {max_value}")
    except ValueError:
        raise ValueError("Введите корректное число")


def show_items(items: Dict[int, str]) -> None:
    """Отображает пункты меню."""
    for i, item in items.items():
        print(f"{i}. {item}")


def format_items(items: Dict[str, Callable], exit_item: Dict[str, Optional[Callable]]) -> Dict[int, str]:
    """Форматирует элементы меню для отображения."""
    all_items = items.copy()
    all_items.update(exit_item)
    return {i: key for i, key in enumerate(all_items.keys(), 1)}


def get_user_choice(title: str, items: Dict[str, Callable], exit_item: Dict[str, Optional[Callable]]) -> None:
    """Получает выбор пользователя и выполняет соответствующее действие."""
    items_dict = format_items(items, exit_item)
    
    while True:
        show_items(items_dict)
        choice = input(f"{title} (1-{len(items_dict)}): ")
        
        try:
            choice_num = validate_choice(choice, len(items_dict))
            selected_item = items_dict.get(choice_num)
            
            # Проверяем, является ли выбранный пункт выходом
            exit_key = list(exit_item.keys())[0]
            if selected_item == exit_key:
                exit_action = exit_item[exit_key]
                if exit_action is not None:
                    return exit_action()
                    
            else:
                # Выполняем выбранное действие
                action = items[selected_item]
                return action()
                
                
        except ValueError as e:
            print(f"Ошибка: {e}")
            print("Попробуйте ещё раз.\n")