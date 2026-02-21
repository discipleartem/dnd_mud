"""
Генераторы характеристик для D&D персонажей.

Поддерживает три метода генерации:
1. Стандартный массив (15, 14, 13, 12, 10, 8)
2. Point Buy (27 очков)
3. Случайные броски (4d6, лучшие 3)
"""

import random
from typing import Dict, List, Tuple, Optional


class AbilityGenerator:
    """Генератор характеристик персонажа."""
    
    # Таблица цен для Point Buy
    POINT_BUY_COSTS = {
        8: 0,
        9: 1,
        10: 2,
        11: 3,
        12: 4,
        13: 5,
        14: 7,
        15: 9
    }
    
    # Названия характеристик на русском
    ABILITY_NAMES = {
        "strength": "Сила",
        "dexterity": "Ловкость", 
        "constitution": "Выносливость",
        "intelligence": "Интеллект",
        "wisdom": "Мудрость",
        "charisma": "Харизма"
    }
    
    def __init__(self):
        """Инициализировать генератор."""
        self.abilities = list(self.ABILITY_NAMES.keys())
    
    def generate_standard_array(self, race_choice: str = None, race_data: Optional[Dict] = None, 
                              subrace_data: Optional[Dict] = None) -> Dict[str, int]:
        """Генерация стандартным массивом."""
        values = [15, 14, 13, 12, 10, 8]
        return self._distribute_abilities(values, "Стандартный массив", race_choice, race_data, subrace_data)
    
    def generate_point_buy(self, race_choice: str = None, race_data: Optional[Dict] = None, 
                         subrace_data: Optional[Dict] = None) -> Dict[str, int]:
        """Сгенерировать характеристики методом Point Buy.
        
        У игрока есть 27 очков для распределения.
        Максимальное значение: 15 (до расовых бонусов)
        Минимальное значение: 8
        """
        return self._point_buy_interface(race_choice, race_data, subrace_data)
    
    def generate_random_dice(self) -> Dict[str, int]:
        """Сгенерировать характеристики случайными бросками.
        
        Для каждой характеристики бросается 4d6, суммируются 3 лучших результата.
        Значения автоматически распределяются по характеристикам.
        """
        print(f"\n🎯 Случайные броски (4d6, лучшие 3)")
        print("Генерируем значения для каждой характеристики...")
        
        result = {}
        rolls_info = []
        
        for ability in self.abilities:
            # Бросаем 4d6 и берем 3 лучших
            rolls = [random.randint(1, 6) for _ in range(4)]
            rolls.sort(reverse=True)
            value = sum(rolls[:3])
            result[ability] = value
            rolls_info.append((self.ABILITY_NAMES[ability], rolls, value))
        
        # Показываем результаты бросков
        print(f"\n📋 Результаты бросков:")
        for ability_name, rolls, value in rolls_info:
            best_rolls = rolls[:3]
            print(f"  {ability_name}: {best_rolls} = {value}")
        
        return result
    
    def _distribute_abilities(self, values: List[int], method_name: str, 
                             race_choice: str = None, race_data: Optional[Dict] = None, 
                             subrace_data: Optional[Dict] = None) -> Dict[str, int]:
        """Распределить значения по характеристикам.
        
        Args:
            values: Список значений для распределения
            method_name: Название метода для отображения
            race_choice: Выбор расы (для отображения бонусов)
            race_data: Данные о расе (для отображения бонусов)
            subrace_data: Данные о подрасе (для отображения бонусов)
            
        Returns:
            Словарь с распределенными характеристиками
        """
        print(f"\n🎲 {method_name}")
        print(f"Доступные значения: {', '.join(map(str, sorted(values, reverse=True)))}")
        
        # Показываем расовые бонусы перед началом распределения
        if race_choice and (race_data or subrace_data):
            print(f"\n💪 Бонусы от расы/подрасы:")
            
            # Базовые бонусы расы
            if race_data:
                base_bonuses = race_data.get("ability_bonuses", {})
                if base_bonuses:
                    bonus_text = self._format_bonuses(base_bonuses)
                    race_name = race_data.get("name", "Раса")
                    print(f"   📍 {race_name}: {bonus_text}")
            
            # Бонусы подрасы
            if subrace_data:
                subrace_bonuses = subrace_data.get("ability_bonuses", {})
                if subrace_bonuses:
                    bonus_text = self._format_bonuses(subrace_bonuses)
                    subrace_name = subrace_data.get("name", "Подраса")
                    print(f"   📍 {subrace_name}: {bonus_text}")
            
            print(f"\n💡 Напоминание: бонусы будут применены ПОСЛЕ распределения значений")
        
        print("\nРаспределите значения по характеристикам:")
        
        result = {}
        remaining_values = values.copy()
        
        for ability in self.abilities:
            ability_name = self.ABILITY_NAMES[ability]
            
            while True:
                # Показываем доступные значения
                print(f"\n{ability_name}:")
                print("Доступные значения:", ", ".join(map(str, sorted(remaining_values, reverse=True))))
                
                try:
                    choice = int(input(f"Выберите значение для {ability_name}: "))
                    if choice in remaining_values:
                        result[ability] = choice
                        remaining_values.remove(choice)
                        break
                    else:
                        print("❌ Такого значения нет в списке доступных.")
                except ValueError:
                    print("❌ Введите число из списка доступных значений.")
        
        # Показываем результат
        print(f"\n✅ Распределение завершено:")
        for ability, value in result.items():
            print(f"  {self.ABILITY_NAMES[ability]}: {value}")
        
        # Показываем расовые бонусы перед подтверждением
        if race_choice and (race_data or subrace_data):
            self._show_race_bonuses_preview(race_choice, race_data, subrace_data, result)
        
        # Подтверждение
        from src.ui.user_choice import get_user_choice
        confirm = get_user_choice(
            ["Да", "Нет"],
            "Подтвердить распределение?",
            allow_cancel=False
        )
        
        if confirm == 2:
            # Перераспределяем заново
            return self._distribute_abilities(values, method_name, race_choice, race_data, subrace_data)
        
        return result
    
    def _point_buy_interface(self, race_choice: str = None, race_data: Optional[Dict] = None, 
                             subrace_data: Optional[Dict] = None) -> Dict[str, int]:
        """Интерфейс для метода Point Buy."""
        print("\n💰 Point Buy")
        print(f"У вас есть 27 очков для распределения")
        print("Таблица цен:")
        
        # Показываем таблицу цен
        for value, cost in sorted(self.POINT_BUY_COSTS.items()):
            print(f"  Значение {value}: {cost} очков")
        
        # Показываем расовые бонусы перед началом распределения
        if race_choice and (race_data or subrace_data):
            print(f"\n💪 Бонусы от расы/подрасы:")
            
            # Базовые бонусы расы
            if race_data:
                base_bonuses = race_data.get("ability_bonuses", {})
                if base_bonuses:
                    bonus_text = self._format_bonuses(base_bonuses)
                    race_name = race_data.get("name", "Раса")
                    print(f"   📍 {race_name}: {bonus_text}")
            
            # Бонусы подрасы
            if subrace_data:
                subrace_bonuses = subrace_data.get("ability_bonuses", {})
                if subrace_bonuses:
                    bonus_text = self._format_bonuses(subrace_bonuses)
                    subrace_name = subrace_data.get("name", "Подраса")
                    print(f"   📍 {subrace_name}: {bonus_text}")
            
            print(f"\n💡 Напоминание: бонусы будут применены ПОСЛЕ распределения очков")
        
        result = {}
        remaining_points = 27
        
        for ability in self.abilities:
            ability_name = self.ABILITY_NAMES[ability]
            
            while True:
                print(f"\n{ability_name}:")
                print(f"Осталось очков: {remaining_points}")
                
                try:
                    value = int(input(f"Выберите значение (8-15): "))
                    if 8 <= value <= 15:
                        cost = self.POINT_BUY_COSTS[value]
                        if cost <= remaining_points:
                            result[ability] = value
                            remaining_points -= cost
                            print(f"✅ Потрачено {cost} очков. Осталось: {remaining_points}")
                            break
                        else:
                            print(f"❌ Недостаточно очков! Нужно {cost}, доступно {remaining_points}")
                    else:
                        print("❌ Значение должно быть от 8 до 15")
                except ValueError:
                    print("❌ Введите число от 8 до 15")
        
        # Показываем результат
        print(f"\n✅ Распределение завершено:")
        total_cost = 0
        for ability, value in result.items():
            cost = self.POINT_BUY_COSTS[value]
            total_cost += cost
            print(f"  {self.ABILITY_NAMES[ability]}: {value} ({cost} очков)")
        
        print(f"\nИтого потрачено: {total_cost} очков")
        
        # Показываем расовые бонусы перед подтверждением
        if race_choice and (race_data or subrace_data):
            self._show_race_bonuses_preview(race_choice, race_data, subrace_data, result)
        
        # Подтверждение
        from src.ui.user_choice import get_user_choice
        confirm = get_user_choice(
            ["Да", "Нет"],
            "Подтвердить распределение?",
            allow_cancel=False
        )
        
        if confirm == 2:
            # Перераспределяем заново
            return self._point_buy_interface(race_choice, race_data, subrace_data)
        
        return result
    
    def get_ability_modifier(self, value: int) -> int:
        """Получить модификатор характеристики."""
        return (value - 10) // 2
    
    def format_ability_with_modifier(self, ability: str, value: int) -> str:
        """Отформатировать характеристику с модификатором."""
        modifier = self.get_ability_modifier(value)
        mod_str = f"+{modifier}" if modifier >= 0 else str(modifier)
        return f"{self.ABILITY_NAMES[ability]}: {value} ({mod_str})"
    
    def _show_race_bonuses_preview(self, race_choice: str, race_data: Optional[Dict], 
                                subrace_data: Optional[Dict], current_abilities: Dict[str, int]) -> None:
        """Показать превью расовых бонусов и итоговых значений."""
        base_race_id = race_choice.split(":")[0]
        
        print(f"\n💪 Расовые бонусы:")
        
        # Базовые бонусы расы
        total_bonuses = {}
        if race_data:
            base_bonuses = race_data.get("ability_bonuses", {})
            if base_bonuses:
                bonus_text = self._format_bonuses(base_bonuses)
                race_name = race_data.get("name", "Раса")
                print(f"   📍 {race_name}: {bonus_text}")
                total_bonuses.update(base_bonuses)
        
        # Бонусы подрасы
        if subrace_data:
            subrace_bonuses = subrace_data.get("ability_bonuses", {})
            if subrace_bonuses:
                bonus_text = self._format_bonuses(subrace_bonuses)
                subrace_name = subrace_data.get("name", "Подраса")
                print(f"   📍 {subrace_name}: {bonus_text}")
                total_bonuses.update(subrace_bonuses)
        
        # Показываем итоговые значения с бонусами
        print(f"\n📋 Итоговые значения с расовыми бонусами:")
        for ability, value in current_abilities.items():
            final_value = value
            if ability in total_bonuses:
                final_value += total_bonuses[ability]
            modifier = self.get_ability_modifier(final_value)
            mod_str = f"+{modifier}" if modifier >= 0 else str(modifier)
            bonus_str = f" +{total_bonuses[ability]}" if ability in total_bonuses else ""
            print(f"   {self.ABILITY_NAMES[ability]}: {value}{bonus_str} = {final_value} ({mod_str})")
    
    def _format_bonuses(self, bonuses: Dict[str, int]) -> str:
        """Отформатировать бонусы."""
        ability_names = {
            "strength": "Сила", "dexterity": "Ловкость", "constitution": "Выносливость",
            "intelligence": "Интеллект", "wisdom": "Мудрость", "charisma": "Харизма"
        }
        
        return ", ".join(f"{ability_names.get(k, k)}+{v}" for k, v in bonuses.items() if v > 0)
