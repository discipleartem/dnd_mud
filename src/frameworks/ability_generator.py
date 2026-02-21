"""Генератор характеристик персонажа.

Находится в слое Frameworks, так как содержит конкретную реализацию
генерации случайных значений.
"""

import random
from typing import Dict, Optional


class AbilityGenerator:
    """Генератор характеристик персонажа."""
    
    # Стоимость очков для Point Buy
    POINT_BUY_COSTS = {
        8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9
    }
    
    # Стандартный массив
    STANDARD_ARRAY = [15, 14, 13, 12, 10, 8]
    
    def generate_standard_array(self, race_choice: str, race_data: Optional[Dict], 
                             subrace_data: Optional[Dict]) -> Dict[str, int]:
        """Сгенерировать характеристики стандартным массивом с интерактивным выбором."""
        abilities = self._get_base_abilities()
        
        # Показываем стандартный массив
        print(f"\n📊 Стандартный массив: {', '.join(map(str, self.STANDARD_ARRAY))}")
        print("\n🎯 Распределите значения по характеристикам:")
        
        # Интерактивное распределение значений
        abilities = self._distribute_standard_array_interactive(abilities)
        
        # Применяем расовые бонусы
        final_abilities = self._apply_race_bonuses_to_abilities(
            abilities, race_choice, race_data, subrace_data
        )
        
        # Показываем финальные характеристики
        print("\n📋 Итоговые характеристики (с расовыми бонусами):")
        for ability, value in final_abilities.items():
            formatted = self.format_ability_with_modifier(ability, value)
            print(f"  {formatted}")
        
        return final_abilities
    
    def generate_point_buy(self, race_choice: str, race_data: Optional[Dict], 
                         subrace_data: Optional[Dict]) -> Dict[str, int]:
        """Сгенерировать характеристики методом Point Buy."""
        abilities = self._get_base_abilities()
        
        print("\n💰 Point Buy (27 очков)")
        print("Стоимость характеристик:")
        print("  8:0  9:1  10:2  11:3  12:4  13:5  14:7  15:9")
        
        # Начинаем со стандартного массива
        for ability, value in zip(abilities.keys(), self.STANDARD_ARRAY):
            abilities[ability] = value
        
        # Применяем расовые бонусы
        abilities = self._apply_race_bonuses_to_abilities(
            abilities, race_choice, race_data, subrace_data
        )
        
        # Показываем финальные характеристики
        print("\n📋 Итоговые характеристики (с расовыми бонусами):")
        for ability, value in abilities.items():
            formatted = self.format_ability_with_modifier(ability, value)
            print(f"  {formatted}")
        
        return abilities
    
    def generate_random_dice(self) -> Dict[str, int]:
        """Сгенерировать характеристики случайными бросками."""
        abilities = self._get_base_abilities()
        
        for ability in abilities:
            # 4d6, лучшие 3
            rolls = sorted([random.randint(1, 6) for _ in range(4)], reverse=True)
            abilities[ability] = sum(rolls[:3])
        
        return abilities
    
    def format_ability_with_modifier(self, ability: str, value: int) -> str:
        """Отформатировать характеристику с модификатором."""
        ability_names = {
            "strength": "Сила", "dexterity": "Ловкость", "constitution": "Выносливость",
            "intelligence": "Интеллект", "wisdom": "Мудрость", "charisma": "Харизма"
        }
        
        modifier = (value - 10) // 2
        modifier_str = f"+{modifier}" if modifier >= 0 else str(modifier)
        
        return f"{ability_names.get(ability, ability)}: {value} ({modifier_str})"
    
    def _get_base_abilities(self) -> Dict[str, int]:
        """Получить базовые характеристики."""
        return {
            "strength": 10,
            "dexterity": 10,
            "constitution": 10,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 10
        }
    
    def _show_race_bonuses_info(self, race_choice: str, race_data: Optional[Dict], 
                               subrace_data: Optional[Dict]) -> None:
        """Показать информацию о расовых бонусах."""
        base_race_id = race_choice.split(":")[0]
        
        print("\n💪 Расовые бонусы:")
        
        # Для альтернативного человека показываем только особую информацию
        if base_race_id == "human" and ":" in race_choice:
            base_race_id, subrace_id = race_choice.split(":", 1)
            if subrace_id == "variant_human":
                print("   📍 Альтернативный человек: выбор 2 характеристик +1")
                return
        
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
    
    def _format_bonuses(self, bonuses: Dict[str, int]) -> str:
        """Отформатировать бонусы."""
        ability_names = {
            "strength": "Сила", "dexterity": "Ловкость", "constitution": "Выносливость",
            "intelligence": "Интеллект", "wisdom": "Мудрость", "charisma": "Харизма"
        }
        
        return ", ".join(f"{ability_names.get(k, k)}+{v}" for k, v in bonuses.items() if v > 0)
    
    def _apply_race_bonuses_to_abilities(self, abilities: Dict[str, int], race_choice: str, 
                                       race_data: Optional[Dict], subrace_data: Optional[Dict]) -> Dict[str, int]:
        """Применить расовые бонусы к характеристикам."""
        base_race_id = race_choice.split(":")[0]
        
        # Проверяем случай альтернативного человека
        if base_race_id == "human" and ":" in race_choice:
            base_race_id, subrace_id = race_choice.split(":", 1)
            if subrace_id == "variant_human":
                return self._handle_variant_human(abilities)
        
        # Для всех остальных рас применяем бонусы автоматически
        result = abilities.copy()
        
        # Базовые бонусы расы
        if race_data:
            bonuses = race_data.get("ability_bonuses", {})
            for ability, bonus in bonuses.items():
                if ability in result:
                    result[ability] += bonus
        
        # Бонусы подрасы
        if subrace_data:
            subrace_bonuses = subrace_data.get("ability_bonuses", {})
            for ability, bonus in subrace_bonuses.items():
                if ability in result:
                    result[ability] += bonus
        
        return result
    
    def _handle_variant_human(self, abilities: Dict[str, int]) -> Dict[str, int]:
        """Обработать альтернативного человека - выбор 2 характеристик +1."""
        print("\n🎯 АЛЬТЕРНАТИВНЫЙ ЧЕЛОВЕК")
        print("="*40)
        print("Выберите 2 характеристики, которые получат бонус +1:")
        
        ability_names = {
            "strength": "Сила", "dexterity": "Ловкость", "constitution": "Выносливость",
            "intelligence": "Интеллект", "wisdom": "Мудрость", "charisma": "Харизма"
        }
        
        available_abilities = list(abilities.keys())
        chosen_abilities = []
        
        for i in range(2):
            print(f"\nВыбор #{i+1}:")
            ability_list = []
            for idx, ability in enumerate(available_abilities):
                if ability not in chosen_abilities:
                    current_value = abilities[ability]
                    ability_list.append(f"{idx+1}. {ability_names[ability]}: {current_value}")
            
            print("\n".join(ability_list))
            
            while True:
                try:
                    choice = int(input(f"Выберите характеристику #{i+1}: "))
                    if 1 <= choice <= len(ability_list):
                        # Получаем индекс из ability_list, а не из available_abilities
                        available_index = 0
                        current_choice = 0
                        for ability in available_abilities:
                            if ability not in chosen_abilities:
                                current_choice += 1
                                if current_choice == choice:
                                    available_index = available_abilities.index(ability)
                                    break
                            available_index += 1
                        
                        ability = available_abilities[available_index]
                        if ability not in chosen_abilities:
                            chosen_abilities.append(ability)
                            print(f"✅ Выбрана: {ability_names[ability]}")
                            break
                        else:
                            print("❌ Эта характеристика уже выбрана.")
                    else:
                        print(f"❌ Выберите число от 1 до {len(ability_list)}")
                except ValueError:
                    print("❌ Введите число.")
        
        # Применяем бонусы
        result = abilities.copy()
        for ability in chosen_abilities:
            result[ability] += 1
        
        print("\n✅ Бонусы применены:")
        for ability in chosen_abilities:
            old_value = abilities[ability]
            new_value = result[ability]
            print(f"  {ability_names[ability]}: {old_value} → {new_value}")
        
        return result
    
    def _distribute_standard_array_interactive(self, abilities: Dict[str, int]) -> Dict[str, int]:
        """Интерактивно распределить значения стандартного массива по характеристикам."""
        ability_names = {
            "strength": "Сила", "dexterity": "Ловкость", "constitution": "Выносливость",
            "intelligence": "Интеллект", "wisdom": "Мудрость", "charisma": "Харизма"
        }
        
        available_values = self.STANDARD_ARRAY.copy()
        assigned_abilities = {}
        
        for i in range(6):
            print(f"\n--- Распределение #{i+1} ---")
            print(f"Доступные значения: {', '.join(map(str, sorted(available_values, reverse=True)))}")
            
            # Показываем доступные характеристики
            print("Доступные характеристики:")
            ability_list = []
            available_ability_keys = []
            for idx, (ability_key, ability_name) in enumerate(ability_names.items()):
                if ability_key not in assigned_abilities:
                    ability_list.append(f"{len(ability_list)+1}. {ability_name}")
                    available_ability_keys.append(ability_key)
            
            print("\n".join(ability_list))
            
            # Выбор характеристики
            while True:
                try:
                    choice = int(input(f"Выберите характеристику #{i+1}: "))
                    if 1 <= choice <= len(ability_list):
                        selected_ability = available_ability_keys[choice - 1]
                        break
                    else:
                        print(f"❌ Выберите число от 1 до {len(ability_list)}")
                except ValueError:
                    print("❌ Введите число.")
            
            # Выбор значения
            print(f"\nДоступные значения для {ability_names[selected_ability]}: {', '.join(map(str, sorted(available_values, reverse=True)))}")
            
            while True:
                try:
                    value_choice = int(input(f"Выберите значение для {ability_names[selected_ability]}: "))
                    if value_choice in available_values:
                        available_values.remove(value_choice)
                        assigned_abilities[selected_ability] = value_choice
                        print(f"✅ {ability_names[selected_ability]}: {value_choice}")
                        break
                    else:
                        print(f"❌ Выберите значение из: {', '.join(map(str, available_values))}")
                except ValueError:
                    print("❌ Введите число.")
        
        # Показываем итоговое распределение
        print("\n📊 Распределенные характеристики:")
        for ability, value in assigned_abilities.items():
            formatted = self.format_ability_with_modifier(ability, value)
            print(f"  {formatted}")
        
        return assigned_abilities