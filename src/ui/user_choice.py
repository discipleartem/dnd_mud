"""
Универсальная система для выбора пользователя.

Модуль предоставляет функцию get_user_choice, которая адаптируется 
под количество переданных элементов и поддерживает различные сценарии использования.
"""

from typing import List, Optional, Tuple, Union


def get_user_choice(
    items: Union[Tuple[str, ...], List[str]], 
    title: str = "",
    prompt: Optional[str] = None,
    allow_cancel: bool = False,
    cancel_text: str = "Отмена"
) -> Optional[int]:
    """Универсальный метод для выбора пользователя.
    
    Args:
        items: Список или кортеж элементов для выбора
        title: Заголовок меню
        prompt: Пользовательский текст приглашения. Если None, генерируется автоматически
        allow_cancel: Разрешить ли отмену выбора (возвращает None)
        cancel_text: Текст для пункта отмены
        
    Returns:
        Номер выбранного элемента (1-based) или None при отмене
        
    Raises:
        ValueError: Если передан пустой список элементов
        
    Examples:
        >>> choice = get_user_choice(["Да", "Нет"], "Подтверждение")
        >>> if choice == 1:
        ...     print("Выбрано: Да")
        
        >>> choice = get_user_choice(["Воин", "Маг", "Лучник"], "Выбор класса", allow_cancel=True)
        >>> if choice is None:
        ...     print("Выбор отменен")
        >>> elif choice == 2:
        ...     print("Выбран класс: Маг")
    """
    if not items:
        raise ValueError("Список элементов не может быть пустым")
    
    while True:
        print("\n" + "="*50)
        if title:
            print(title.center(50))
        print("="*50)
        
        # Отображаем все пункты меню
        for i, item in enumerate(items, 1):
            print(f"{i}. {item}")
        
        # Добавляем пункт отмены если нужно
        if allow_cancel:
            cancel_index = len(items) + 1
            print(f"{cancel_index}. {cancel_text}")
            max_choice = cancel_index
        else:
            max_choice = len(items)
        
        print("="*50)
        
        # Формируем приглашение для ввода
        if prompt is None:
            prompt_text = f"Выберите пункт (1-{max_choice})"
        else:
            prompt_text = prompt
            
        choice = input(f"{prompt_text}: ").strip()
        
        # Обработка отмены
        if allow_cancel and choice == str(cancel_index):
            return None
            
        # Проверка валидности выбора
        if choice.isdigit() and 1 <= int(choice) <= len(items):
            return int(choice)  # Возвращаем 1-based индекс
        else:
            print(f"❌ Неверный выбор. Введите число от 1 до {max_choice}.")
