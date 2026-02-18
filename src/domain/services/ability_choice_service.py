# src/domain/services/ability_choice_service.py
"""
Сервис для работы с выбором характеристик у рас.

Применяемые паттерны:
- Service (Сервис) - инкапсулирует логику выбора характеристик
- Strategy (Стратегия) - разные стратегии выбора для разных рас

Применяемые принципы:
- Single Responsibility -专注于 выборе характеристик
- Open/Closed - легко добавить новые стратегии выбора
- Dependency Inversion - работает с абстракцией Race
"""

from typing import List, Dict, Tuple, Optional
from ..entities.race import Race


class AbilityChoiceService:
    """Сервис для работы с выбором характеристик."""
    
    @staticmethod
    def get_choice_info(race: Race) -> Dict[str, any]:
        """Получает информацию о выборе характеристик для расы.
        
        Args:
            race: Раса персонажа
            
        Returns:
            Словарь с информацией о выборе
        """
        if not race.has_ability_choice():
            return {
                "has_choice": False,
                "max_choices": 0,
                "allowed_attributes": [],
                "bonus_value": 0,
                "features": []
            }
        
        features = race.get_ability_choice_features()
        max_choices = race.get_max_ability_choices()
        allowed_attributes = race.get_allowed_attributes()
        
        # Определяем значение бонуса (берем из первой особенности)
        bonus_value = 1
        if features:
            bonus_value = features[0].get("bonus_value", 1)
        
        return {
            "has_choice": True,
            "max_choices": max_choices,
            "allowed_attributes": allowed_attributes,
            "bonus_value": bonus_value,
            "features": features
        }
    
    @staticmethod
    def format_choice_menu(choice_info: Dict[str, any]) -> str:
        """Форматирует меню выбора характеристик.
        
        Args:
            choice_info: Информация о выборе от get_choice_info
            
        Returns:
            Отформатированная строка меню
        """
        if not choice_info["has_choice"]:
            return "У этой расы нет выбора характеристик."
        
        max_choices = choice_info["max_choices"]
        bonus_value = choice_info["bonus_value"]
        allowed = choice_info["allowed_attributes"]
        
        # Словарь с русскими названиями
        russian_names = {
            "strength": "Сила",
            "dexterity": "Ловкость", 
            "constitution": "Телосложение",
            "intelligence": "Интеллект",
            "wisdom": "Мудрость",
            "charisma": "Харизма"
        }
        
        lines = [
            f"Выберите {max_choices} характеристик (+{bonus_value} к каждой):",
            ""
        ]
        
        for i, attr in enumerate(allowed, 1):
            russian_name = russian_names.get(attr, attr.title())
            lines.append(f"{i}. {russian_name}")
        
        lines.append("")
        lines.append(f"Введите номера через запятую (например: 1,3)")
        
        return "\n".join(lines)
    
    @staticmethod
    def parse_choice_input(user_input: str, allowed_attributes: List[str]) -> List[str]:
        """Парсит ввод пользователя и возвращает выбранные характеристики.
        
        Args:
            user_input: Строка ввода пользователя
            allowed_attributes: Список допустимых характеристик
            
        Returns:
            Список выбранных характеристик
        """
        if not user_input.strip():
            return []
        
        try:
            # Разбиваем ввод по запятым
            numbers = [int(x.strip()) for x in user_input.split(",")]
            
            # Конвертируем номера в названия характеристик
            chosen = []
            for num in numbers:
                if 1 <= num <= len(allowed_attributes):
                    chosen.append(allowed_attributes[num - 1])
            
            return chosen
        except (ValueError, IndexError):
            return []
    
    @staticmethod
    def validate_choice(chosen_attributes: List[str], 
                     max_choices: int, 
                     allowed_attributes: List[str]) -> Tuple[bool, str]:
        """Валидирует выбор характеристик.
        
        Args:
            chosen_attributes: Выбранные характеристики
            max_choices: Максимальное количество выборов
            allowed_attributes: Разрешенные характеристики
            
        Returns:
            Кортеж (валидно, сообщение_об_ошибке)
        """
        if len(chosen_attributes) > max_choices:
            return False, f"Можно выбрать не более {max_choices} характеристик"
        
        if len(chosen_attributes) == 0:
            return False, "Нужно выбрать хотя бы одну характеристику"
        
        # Проверяем что все выбранные характеристики разрешены
        invalid = [attr for attr in chosen_attributes if attr not in allowed_attributes]
        if invalid:
            return False, f"Недопустимые характеристики: {', '.join(invalid)}"
        
        # Проверяем на дубликаты
        if len(chosen_attributes) != len(set(chosen_attributes)):
            return False, "Нельзя выбирать одну характеристику дважды"
        
        return True, ""
    
    @staticmethod
    def get_default_choice(race: Race) -> List[str]:
        """Возвращает выбор характеристик по умолчанию.
        
        Args:
            race: Раса персонажа
            
        Returns:
            Список характеристик по умолчанию
        """
        if not race.has_ability_choice():
            return []
        
        max_choices = race.get_max_ability_choices()
        allowed = race.get_allowed_attributes()
        
        # По умолчанию выбираем первые max_choices характеристик
        return allowed[:max_choices]
