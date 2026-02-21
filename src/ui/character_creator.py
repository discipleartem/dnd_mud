"""
Простой интерфейс создания персонажа.

Следует принципу KISS - минимум кода, максимум функциональности.
"""

from typing import Dict, List, Optional, Tuple

from src.ui.user_choice import get_user_choice
from src.services.character_service import CharacterService, CreateCharacterResponse
from src.services.ability_generator import AbilityGenerator
from src.models.data import Character
from src.data.repositories import SizeRepository


class CharacterCreator:
    """Простой создатель персонажей."""
    
    def __init__(self):
        self.service = CharacterService()
        self.size_repo = SizeRepository()
        self.ability_generator = AbilityGenerator()
    
    def create_character(self) -> Optional[Character]:
        """Запустить процесс создания персонажа."""
        print("\n" + "="*60)
        print("СОЗДАНИЕ ПЕРСОНАЖА".center(60))
        print("="*60)
        
        try:
            # Шаг 1: Имя
            name = self._get_name()
            if not name:
                return None
            
            # Шаг 2: Раса
            race_choice = self._get_race()
            if not race_choice:
                return None
            
            # Шаг 3: Характеристики с учетом расовых бонусов
            abilities = self._get_abilities(race_choice)
            if not abilities:
                return None
            
            # Шаг 4: Класс
            class_choice = self._get_class()
            if not class_choice:
                return None
            
            # Создание персонажа
            response = self.service.create_character(name, race_choice, class_choice, abilities)
            
            if response.success:
                self._display_character(response.character)
                return response.character
            else:
                print("\n❌ Ошибки при создании персонажа:")
                for error in response.errors:
                    print(f"  - {error}")
                return None
                
        except KeyboardInterrupt:
            print("\n\n⚠️ Создание персонажа отменено.")
            return None
    
    def _get_name(self) -> Optional[str]:
        """Получить имя персонажа."""
        while True:
            name = input("\nВведите имя персонажа (или 'отмена' для выхода): ").strip()
            
            if name.lower() == 'отмена':
                return None
            
            if not name:
                print("❌ Имя не может быть пустым.")
                continue
            
            if get_user_choice(["Да", "Нет"], f"Имя '{name}' подходит?", allow_cancel=False) == 1:
                return name
    
    def _get_race(self) -> Optional[str]:
        """Получить выбор расы."""
        races = self.service.get_race_choices()
        race_ids = [race[0] for race in races]
        
        # Создаем расширенное меню с эмодзи и бонусами
        enhanced_race_menu = self._create_enhanced_race_menu(races)
        
        choice = get_user_choice(enhanced_race_menu, "🧬 ВЫБЕРИТЕ РАСУ:", allow_cancel=True)
        if choice is None:
            return None
        
        race_id = race_ids[choice - 1]
        
        # Показываем информацию о расе
        self._show_race_info(race_id)
        
        # Проверяем подрасы
        subraces = self.service.get_subrace_choices(race_id)
        if not subraces:
            return race_id
        
        # Для эльфов всегда требуем выбрать подрасу
        if race_id == "elf":
            # Предлагаем только выбор подрасы
            subrace_choice = get_user_choice(
                [f"Выбрать: {sub[1]}" for sub in subraces],
                "Выберите подрасу эльфа:",
                allow_cancel=True
            )
            
            if subrace_choice is None:
                return None
            
            subrace_id = subraces[subrace_choice - 1][0]
            subrace_name = subraces[subrace_choice - 1][1]
            self._show_subrace_info(race_id, subrace_id)
            
            # Подтверждение выбора подрасы
            confirm = get_user_choice(
                ["Да", "Нет"],
                f"Выбрать подрасу '{subrace_name}'?",
                allow_cancel=False
            )
            
            if confirm == 1:
                return f"{race_id}:{subrace_id}"
            else:
                # Возвращаемся к выбору подрасы
                return self._get_race()
        else:
            # Для других рас предлагаем выбор с опцией базовой расы
            subrace_choice = get_user_choice(
                ["Продолжить с базовой расой"] + [f"Выбрать: {sub[1]}" for sub in subraces],
                "Выберите вариант:",
                allow_cancel=False
            )
            
            if subrace_choice == 1:
                return race_id
            else:
                subrace_id = subraces[subrace_choice - 2][0]
                subrace_name = subraces[subrace_choice - 2][1]
                self._show_subrace_info(race_id, subrace_id)
                
                # Подтверждение выбора подрасы
                confirm = get_user_choice(
                    ["Да", "Нет"],
                    f"Выбрать подрасу '{subrace_name}'?",
                    allow_cancel=False
                )
                
                if confirm == 1:
                    return f"{race_id}:{subrace_id}"
                else:
                    # Возвращаемся к выбору подрасы
                    return self._get_race()
    
    def _create_enhanced_race_menu(self, races: List[Tuple[str, str]]) -> List[str]:
        """Создать расширенное меню рас с эмодзи и бонусами."""
        race_emojis = {
            "human": "👥",
            "elf": "🧝", 
            "half_orc": "👹"
        }
        
        enhanced_menu = []
        for race_id, race_name in races:
            emoji = race_emojis.get(race_id, "🎭")
            
            # Получаем описание бонусов для расы
            race_data = self.service.get_race_details(race_id)
            bonuses_text = ""
            if race_data and race_data.get('ability_bonuses_description'):
                bonuses_text = f" [{race_data['ability_bonuses_description']}]"
            
            enhanced_menu.append(f"{emoji} {race_name}{bonuses_text}")
        
        return enhanced_menu
    
    def _show_race_info(self, race_id: str) -> None:
        """Показать информацию о расе."""
        race_data = self.service.get_race_details(race_id)
        if not race_data:
            return
        
        print(f"\n📖 {race_data['name']}")
        print(f"   {race_data['description']}")
        
        # Базовые бонусы расы
        bonuses_description = race_data.get('ability_bonuses_description', '')
        if bonuses_description:
            print(f"💪 Бонусы расы: {bonuses_description}")
        else:
            # Fallback на старый формат если описание отсутствует
            bonuses = race_data.get('ability_bonuses', {})
            if bonuses:
                bonus_text = self._format_bonuses(bonuses)
                print(f"💪 Бонусы расы: {bonus_text}")
            else:
                print(f"💪 Бонусы расы: нет")
        
        size_key = race_data.get('size', 'N/A')
        size_name = self.size_repo.get_size_name(size_key) if size_key != 'N/A' else 'N/A'
        print(f"📏 Размер: {size_name}")
        print(f"🏃 Скорость: {race_data.get('speed', 'N/A')} футов")
        
        # Показываем доступные подрасы и их бонусы
        subraces = self.service.get_subrace_choices(race_id)
        if subraces:
            if race_id == "elf":
                print(f"\n🌟 Необходимо выбрать подрасу эльфа:")
            else:
                print(f"\n🌟 Доступные подрасы:")
            for subrace_id, subrace_name in subraces:
                subrace_data = self.service.get_subrace_details(race_id, subrace_id)
                if subrace_data:
                    bonuses_description = subrace_data.get('ability_bonuses_description', '')
                    if bonuses_description:
                        print(f"   📍 {subrace_name}: {bonuses_description}")
                    else:
                        # Fallback на старый формат
                        subrace_bonuses = subrace_data.get('ability_bonuses', {})
                        if subrace_bonuses:
                            bonus_text = self._format_bonuses(subrace_bonuses)
                            print(f"   📍 {subrace_name}: {bonus_text}")
                        else:
                            print(f"   📍 {subrace_name}: нет бонусов к характеристикам")
        else:
            print(f"\n🌟 Подрасы: отсутствуют")
    
    def _show_subrace_info(self, race_id: str, subrace_id: str) -> None:
        """Показать информацию о подрасе."""
        subrace_data = self.service.get_subrace_details(race_id, subrace_id)
        if not subrace_data:
            return
        
        # Получаем базовую информацию о расе для контекста
        race_data = self.service.get_race_details(race_id)
        
        print(f"\n📖 {subrace_data['name']}")
        print(f"   {subrace_data['description']}")
        
        # Бонусы подрасы
        subrace_bonuses_description = subrace_data.get('ability_bonuses_description', '')
        subrace_bonuses = subrace_data.get('ability_bonuses', {})
        
        # Для альтернативного человека не показываем дополнительные бонусы отдельно,
        # так как они будут показаны в общих бонусах
        if not (race_id == "human" and subrace_id == "variant_human"):
            if subrace_bonuses_description:
                print(f"💪 Дополнительные бонусы: {subrace_bonuses_description}")
            else:
                # Fallback на старый формат
                if subrace_bonuses:
                    bonus_text = self._format_bonuses(subrace_bonuses)
                    print(f"💪 Дополнительные бонусы: {bonus_text}")
                else:
                    print(f"💪 Дополнительные бонусы: нет")
        
        # Показываем общие бонусы (базовая раса + подраса)
        if race_data:
            base_bonuses = race_data.get('ability_bonuses', {})
            
            # Для альтернативного человека не добавляем базовые бонусы, так как они переопределены
            if race_id == "human" and subrace_id == "variant_human":
                # Используем описание бонусов подрасы для альтернативного человека
                subrace_bonuses_description = subrace_data.get('ability_bonuses_description', '')
                if subrace_bonuses_description:
                    print(f"🎯 Общие бонусы: {subrace_bonuses_description}")
                else:
                    # Fallback на подсчет bonuses
                    total_bonuses = subrace_bonuses.copy()
                    if total_bonuses:
                        total_bonus_text = self._format_bonuses(total_bonuses)
                        print(f"🎯 Общие бонусы: {total_bonus_text}")
            else:
                total_bonuses = base_bonuses.copy()
                # Суммируем бонусы
                for ability, bonus in subrace_bonuses.items():
                    if ability in total_bonuses:
                        total_bonuses[ability] += bonus
                    else:
                        total_bonuses[ability] = bonus
                
                if total_bonuses:
                    total_bonus_text = self._format_bonuses(total_bonuses)
                    print(f"🎯 Общие бонусы (раса + подраса): {total_bonus_text}")
        
        # Показываем особенности подрасы
        features = subrace_data.get('features', [])
        if features:
            print(f"\n⚡ Особенности подрасы:")
            for feature in features:
                print(f"   • {feature.get('name', 'Без названия')}: {feature.get('description', 'Нет описания')}")
        
        # Показываем базовую информацию от расы
        if race_data:
            size_key = race_data.get('size', 'N/A')
            size_name = self.size_repo.get_size_name(size_key) if size_key != 'N/A' else 'N/A'
            print(f"\n📏 Размер: {size_name}")
            print(f"🏃 Скорость: {race_data.get('speed', 'N/A')} футов")
    
    def _format_bonuses(self, bonuses: Dict[str, int]) -> str:
        """Отформатировать бонусы."""
        ability_names = {
            "strength": "Сила", "dexterity": "Ловкость", "constitution": "Выносливость",
            "intelligence": "Интеллект", "wisdom": "Мудрость", "charisma": "Харизма"
        }
        
        return ", ".join(f"{ability_names.get(k, k)}+{v}" for k, v in bonuses.items() if v > 0)
    
    def _show_race_bonuses_info(self, race_choice: str, race_data: Optional[Dict], subrace_data: Optional[Dict]) -> None:
        """Показать информацию о расовых бонусах."""
        base_race_id = race_choice.split(":")[0]
        
        print(f"\n💪 Расовые бонусы:")
        
        # Для альтернативного человека показываем только особую информацию
        if base_race_id == "human" and ":" in race_choice:
            base_race_id, subrace_id = race_choice.split(":", 1)
            if subrace_id == "variant_human":
                print(f"   📍 Альтернативный человек: выбор 2 характеристик +1")
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
    
    def _get_class(self) -> Optional[str]:
        """Получить выбор класса."""
        classes = self.service.get_class_choices()
        class_ids = [cls[0] for cls in classes]
        class_names = [cls[1] for cls in classes]
        
        choice = get_user_choice(class_names, "⚔️ ВЫБЕРИТЕ КЛАСС:", allow_cancel=True)
        if choice is None:
            return None
        
        return class_ids[choice - 1]
    
    def _get_abilities(self, race_choice: str) -> Optional[Dict[str, int]]:
        """Получить характеристики с выбором метода генерации и применением расовых бонусов."""
        print("\n🎲 ГЕНЕРАЦИЯ ХАРАКТЕРИСТИК")
        print("="*50)
        
        # Получаем данные о расе для информации о бонусах
        race_data = self.service.get_race_details(race_choice.split(":")[0])
        subrace_data = None
        if ":" in race_choice:
            base_race_id, subrace_id = race_choice.split(":", 1)
            subrace_data = self.service.get_subrace_details(base_race_id, subrace_id)
        
        choice = get_user_choice(
            [
                "📊 Стандартный массив (15, 14, 13, 12, 10, 8)",
                "💰 Point Buy (27 очков)",
                "🎯 Случайные броски (4d6, лучшие 3)"
            ],
            "Выберите метод генерации характеристик:",
            allow_cancel=True
        )
        
        if choice is None:
            return None
        
        try:
            if choice == 1:
                # Стандартный массив
                abilities = self.ability_generator.generate_standard_array(race_choice, race_data, subrace_data)
                
            elif choice == 2:
                # Point Buy
                abilities = self.ability_generator.generate_point_buy(race_choice, race_data, subrace_data)
                
            elif choice == 3:
                # Случайные броски - без перегенерации
                abilities = self.ability_generator.generate_random_dice()
                
            else:
                return None
            
            # Показываем начальные характеристики (только для случайных бросков)
            if choice == 3:
                print(f"\n📊 Начальные характеристики:")
                for ability, value in abilities.items():
                    formatted = self.ability_generator.format_ability_with_modifier(ability, value)
                    print(f"  {formatted}")
                
                # Показываем расовые бонусы
                self._show_race_bonuses_info(race_choice, race_data, subrace_data)
                
                # Применяем расовые бонусы
                abilities = self._apply_race_bonuses_to_abilities(abilities, race_choice, race_data, subrace_data)
                
                # Показываем финальные характеристики с модификаторами
                print(f"\n📋 Итоговые характеристики (с расовыми бонусами):")
                for ability, value in abilities.items():
                    formatted = self.ability_generator.format_ability_with_modifier(ability, value)
                    print(f"  {formatted}")
            else:
                # Для стандартного массива и Point Buy бонусы уже показаны в методах генерации
                # Применяем расовые бонусы
                abilities = self._apply_race_bonuses_to_abilities(abilities, race_choice, race_data, subrace_data)
            
            # Подтверждение (только для методов с выбором)
            if choice != 3:  # Не для случайных бросков
                confirm = get_user_choice(
                    ["Да", "Перегенерировать"],
                    "Подтвердить характеристики?",
                    allow_cancel=False
                )
                
                if confirm == 2:
                    return self._get_abilities(race_choice)
            else:
                print(f"\n✅ Характеристики сгенерированы и приняты.")
            
            return abilities
            
        except KeyboardInterrupt:
            print("\n⚠️ Генерация характеристик отменена.")
            return None
    
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
        print(f"\n🎯 АЛЬТЕРНАТИВНЫЙ ЧЕЛОВЕК")
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
        
        print(f"\n✅ Бонусы применены:")
        for ability in chosen_abilities:
            old_value = abilities[ability]
            new_value = result[ability]
            print(f"  {ability_names[ability]}: {old_value} → {new_value}")
        
        return result
    
    def _display_character(self, character: Character) -> None:
        """Отобразить созданного персонажа."""
        print("\n" + "="*60)
        print("ПЕРСОНАЖ СОЗДАН!".center(60))
        print("="*60)
        print(character)
        print("="*60)
