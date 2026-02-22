from typing import Dict, Callable, Optional


def validate_choice(choice: str, max_value: int) -> int:
    """Проверяет корректность выбора пользователя.
    
    Args:
        choice: Строка с выбором пользователя
        max_value: Максимальное допустимое значение
        
    Returns:
        int: Валидированный номер выбора
        
    Raises:
        ValueError: Если выбор некорректен
    """
    if not choice.strip():
        raise ValueError("Пустой ввод")
    
    try:
        choice_num = int(choice)
    except ValueError:
        raise ValueError("Введите число")
    
    if not 1 <= choice_num <= max_value:
        raise ValueError(f"Число должно быть от 1 до {max_value}")
    
    return choice_num


def show_items(items: Dict[int, str]) -> None:
    """Отображает пункты меню."""
    for i, item in items.items():
        print(f"{i}. {item}")


def format_items(items: Dict[str, Callable], exit_item: Dict[str, Optional[Callable]]) -> Dict[int, str]:
    """Форматирует элементы меню для отображения."""
    all_items = {**items, **exit_item}
    return {i: key for i, key in enumerate(all_items.keys(), 1)}


def get_user_choice(title: str, items: Dict[str, Callable], exit_item: Dict[str, Optional[Callable]]) -> None:
    """Получает выбор пользователя и выполняет соответствующее действие.
    
    Args:
        title: Заголовок меню
        items: Словарь с пунктами меню и их функциями
        exit_item: Словарь с пунктом выхода
    """
    items_dict = format_items(items, exit_item)
    exit_key = next(iter(exit_item))  # Получаем ключ выхода один раз
    
    while True:
        show_items(items_dict)
        choice = input(f"{title} (1-{len(items_dict)}): ")
        
        try:
            choice_num = validate_choice(choice, len(items_dict))
            selected_item = items_dict[choice_num]
            
            if selected_item == exit_key:
                exit_item[exit_key]()
                return
            
            items[selected_item]()
            return
                
        except ValueError as e:
            print(f"Ошибка: {e}")
            print("Попробуйте ещё раз.\n")