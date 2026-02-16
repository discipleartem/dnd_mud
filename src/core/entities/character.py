"""
Модуль персонажа D&D MUD.

Определяет базовый класс персонажа и его характеристики.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional
from ..mechanics.attributes import StandardAttributes
from ..mechanics.skills import SkillsManager
from .attribute import Attribute
from .race import Race
from .race_factory import RaceFactory
from .class_ import CharacterClass
from .class_factory import CharacterClassFactory
from .skill import Skill


@dataclass
class Character:
    """Класс персонажа D&D."""
    
    # Базовая информация
    name: str = field(default="Безымянный")
    level: int = field(default=1)
    race: Race = field(default_factory=lambda: RaceFactory.create_race("human"))
    character_class: CharacterClass = field(default_factory=lambda: CharacterClassFactory.create_class("fighter"))
    
    # Характеристики
    strength: Attribute = field(default_factory=lambda: Attribute(name='strength', value=StandardAttributes.get_attribute('strength').default_value))
    dexterity: Attribute = field(default_factory=lambda: Attribute(name='dexterity', value=StandardAttributes.get_attribute('dexterity').default_value))
    constitution: Attribute = field(default_factory=lambda: Attribute(name='constitution', value=StandardAttributes.get_attribute('constitution').default_value))
    intelligence: Attribute = field(default_factory=lambda: Attribute(name='intelligence', value=StandardAttributes.get_attribute('intelligence').default_value))
    wisdom: Attribute = field(default_factory=lambda: Attribute(name='wisdom', value=StandardAttributes.get_attribute('wisdom').default_value))
    charisma: Attribute = field(default_factory=lambda: Attribute(name='charisma', value=StandardAttributes.get_attribute('charisma').default_value))
    
    # Производные характеристики
    hp_max: int = field(default=10)
    hp_current: int = field(default=10)
    ac: int = field(default=10)
    gold: int = field(default=0)
    
    # Навыки (инициализируются лениво)
    _skills: Optional[Dict[str, Skill]] = field(default=None, init=False)
    
    # Владение спасбросками (инициализируются лениво)
    _save_proficiencies: Optional[Dict[str, bool]] = field(default=None, init=False)

    def __post_init__(self) -> None:
        """Валидация персонажа."""
        if self.level < 1:
            raise ValueError(f"Уровень персонажа должен быть не менее 1, получено: {self.level}")
        
        # Валидируем все характеристики
        for attr_name in ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']:
            attr = getattr(self, attr_name)
            if hasattr(attr, 'validate'):
                attr.validate()


    def __getattr__(self, name: str) -> int:
            """Динамический доступ к характеристикам."""
            # Ищем в стандартах
            for attr_name, standard_attr in StandardAttributes.get_all().items():
                if standard_attr.short_name == name:
                    return getattr(self, attr_name).value
            
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")


    def __setattr__(self, name: str, value: int) -> None:
        """Динамическая запись характеристик."""
        if name in ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']:
            attribute_map = {
                'STR': 'strength', 'DEX': 'dexterity', 'CON': 'constitution',
                'INT': 'intelligence', 'WIS': 'wisdom', 'CHA': 'charisma'
            }
            getattr(self, attribute_map[name]).value = value
        else:
            super().__setattr__(name, value)
    
    def apply_race_bonuses(self) -> None:
        """Применяет расовые бонусы к характеристикам."""
        attributes = {
            'strength': self.strength.value,
            'dexterity': self.dexterity.value,
            'constitution': self.constitution.value,
            'intelligence': self.intelligence.value,
            'wisdom': self.wisdom.value,
            'charisma': self.charisma.value
        }
        
        boosted_attributes = self.race.apply_bonuses(attributes)
        
        # Обновляем значения характеристик
        for attr_name, value in boosted_attributes.items():
            getattr(self, attr_name).value = value
    
    def get_ability_modifier(self, value: int) -> int:
        """Рассчитывает модификатор характеристики.
        
        Args:
            value: Значение характеристики
            
        Returns:
            Модификатор (значение - 10) // 2
        """
        return (value - 10) // 2
    
    def get_all_modifiers(self) -> Dict[str, int]:
        """Возвращает словарь всех модификаторов характеристик."""
        return {
            'strength': self.get_ability_modifier(self.strength.value),
            'dexterity': self.get_ability_modifier(self.dexterity.value),
            'constitution': self.get_ability_modifier(self.constitution.value),
            'intelligence': self.get_ability_modifier(self.intelligence.value),
            'wisdom': self.get_ability_modifier(self.wisdom.value),
            'charisma': self.get_ability_modifier(self.charisma.value)
        }
    
    def calculate_hp(self) -> int:
        """Рассчитывает максимальное HP на основе класса и телосложения."""
        return self.character_class.calculate_hp(self.constitution.value)
    
    def calculate_ac(self) -> int:
        """Рассчитывает класс доспеха."""
        # Базовый AC = 10 + модификатор ловкости
        base_ac = 10 + self.get_ability_modifier(self.dexterity.value)
        
        # Добавляем бонус от класса если есть
        base_ac += self.character_class.get_ac_bonus()
        
        return base_ac
    
    def calculate_derived_stats(self) -> None:
        """Рассчитывает все производные характеристики."""
        self.hp_max = self.calculate_hp()
        self.hp_current = self.hp_max
        self.ac = self.calculate_ac()
    
    # === Методы работы с навыками ===
    
    @property
    def skills(self) -> Dict[str, Skill]:
        """Возвращает словарь навыков персонажа (ленивая инициализация)."""
        if self._skills is None:
            self._skills = {}
            # Создаем все навыки из конфигурации
            for skill_name in SkillsManager.get_all_skills():
                self._skills[skill_name] = Skill(name=skill_name)
        return self._skills
    
    def get_skill(self, skill_name: str) -> Optional[Skill]:
        """Возвращает навык по имени."""
        return self.skills.get(skill_name)
    
    def get_skill_bonus(self, skill_name: str) -> int:
        """Рассчитывает общий бонус к навыку."""
        skill = self.get_skill(skill_name)
        if not skill:
            return 0
        
        # Получаем значения характеристик
        attributes = {
            'strength': self.strength.value,
            'dexterity': self.dexterity.value,
            'constitution': self.constitution.value,
            'intelligence': self.intelligence.value,
            'wisdom': self.wisdom.value,
            'charisma': self.charisma.value
        }
        
        return skill.calculate_total_bonus(attributes, self.get_proficiency_bonus())
    
    def get_saving_throw_bonus(self, attribute: str) -> int:
        """Рассчитывает бонус к спасброску характеристики."""
        # Создаем временный навык-спасбросок
        save_config = SkillsManager.get_saving_throw(attribute)
        if not save_config:
            return 0
        
        # Проверяем, имеет ли персонаж мастерство в спасброске
        proficiency_bonus = self.get_proficiency_bonus() if self.has_save_proficiency(attribute) else 0
        
        # Модификатор характеристики
        attribute_value = getattr(self, attribute).value
        attribute_modifier = (attribute_value - 10) // 2
        
        return attribute_modifier + proficiency_bonus
    
    def get_proficiency_bonus(self) -> int:
        """Возвращает бонус мастерства персонажа."""
        return 1 + (self.level // 4)  # +2 на 1-4 уровне, +3 на 5-8, и т.д.
    
    def has_save_proficiency(self, attribute: str) -> bool:
        """Проверяет, имеет ли персонаж мастерство в спасброске."""
        if self._save_proficiencies is None:
            self._save_proficiencies = {}
            # Инициализируем базовые владения спасбросками
            self._initialize_save_proficiencies()
        
        return self._save_proficiencies.get(attribute, False)
    
    def _initialize_save_proficiencies(self) -> None:
        """Инициализирует владение спасбросками от класса и расы."""
        # TODO: Получить владения от класса персонажа
        # Пока используем базовые владения для воина (Сила и Телосложение)
        class_saves = self.character_class.get_save_proficiencies()
        
        # TODO: Получить владения от расы
        race_saves = self.race.get_save_proficiencies() if hasattr(self.race, 'get_save_proficiencies') else []
        
        # Объединяем владения
        all_saves = set(class_saves + race_saves)
        
        for attr in all_saves:
            self._save_proficiencies[attr] = True
    
    def add_save_proficiency(self, attribute: str) -> None:
        """Добавляет владение спасброском."""
        if self._save_proficiencies is None:
            self._initialize_save_proficiencies()
        
        if SkillsManager.is_valid_saving_throw(attribute):
            self._save_proficiencies[attribute] = True
    
    def remove_save_proficiency(self, attribute: str) -> None:
        """Удаляет владение спасброском."""
        if self._save_proficiencies is not None:
            self._save_proficiencies[attribute] = False
    
    def get_save_proficiencies(self) -> Dict[str, bool]:
        """Возвращает все владения спасбросками."""
        if self._save_proficiencies is None:
            self._initialize_save_proficiencies()
        return self._save_proficiencies.copy()
    
    def add_skill_proficiency(self, skill_name: str) -> None:
        """Добавляет мастерство в навык."""
        skill = self.get_skill(skill_name)
        if skill:
            skill.add_proficiency(self.get_proficiency_bonus())
    
    def add_skill_expertise(self, skill_name: str) -> None:
        """Добавляет экспертизу в навык."""
        skill = self.get_skill(skill_name)
        if skill:
            skill.add_expertise(self.get_proficiency_bonus() * 2)
    
    def remove_skill_proficiency(self, skill_name: str) -> None:
        """Удаляет мастерство из навыка."""
        skill = self.get_skill(skill_name)
        if skill:
            skill.remove_proficiency()
    
    def get_skills_by_attribute(self, attribute: str) -> Dict[str, Skill]:
        """Возвращает навыки, использующие указанную характеристику."""
        return {name: skill for name, skill in self.skills.items() 
                if skill.attribute_name == attribute}
    
    def roll_skill_check(self, skill_name: str, advantage: str = "none", situational_bonus: int = 0) -> tuple:
        """Выполняет бросок навыка.
        
        Args:
            skill_name: Имя навыка
            advantage: "advantage", "disadvantage", или "none"
            situational_bonus: Ситуационный бонус/штраф
            
        Returns:
            Кортеж (бросок_d20, общий_результат, крит_успех, крит_провал)
        """
        import random
        
        skill_bonus = self.get_skill_bonus(skill_name)
        
        # Бросок с преимуществом/помехой
        if advantage == "advantage":
            d20_1 = random.randint(1, 20)
            d20_2 = random.randint(1, 20)
            d20_roll = max(d20_1, d20_2)
            crit_success = d20_roll == 20
            crit_fail = d20_roll == 1
        elif advantage == "disadvantage":
            d20_1 = random.randint(1, 20)
            d20_2 = random.randint(1, 20)
            d20_roll = min(d20_1, d20_2)
            crit_success = d20_roll == 20
            crit_fail = d20_roll == 1
        else:  # normal roll
            d20_roll = random.randint(1, 20)
            crit_success = d20_roll == 20
            crit_fail = d20_roll == 1
        
        total = d20_roll + skill_bonus + situational_bonus
        
        return d20_roll, total, crit_success, crit_fail
    
    def roll_saving_throw(self, attribute: str, advantage: str = "none", situational_bonus: int = 0) -> tuple:
        """Выполняет спасбросок характеристики.
        
        Args:
            attribute: Характеристика для спасброска
            advantage: "advantage", "disadvantage", или "none"
            situational_bonus: Ситуационный бонус/штраф
            
        Returns:
            Кортеж (бросок_d20, общий_результат, крит_успех, крит_провал)
        """
        import random
        
        save_bonus = self.get_saving_throw_bonus(attribute)
        
        # Бросок с преимуществом/помехой
        if advantage == "advantage":
            d20_1 = random.randint(1, 20)
            d20_2 = random.randint(1, 20)
            d20_roll = max(d20_1, d20_2)
            crit_success = d20_roll == 20
            crit_fail = d20_roll == 1
        elif advantage == "disadvantage":
            d20_1 = random.randint(1, 20)
            d20_2 = random.randint(1, 20)
            d20_roll = min(d20_1, d20_2)
            crit_success = d20_roll == 20
            crit_fail = d20_roll == 1
        else:  # normal roll
            d20_roll = random.randint(1, 20)
            crit_success = d20_roll == 20
            crit_fail = d20_roll == 1
        
        total = d20_roll + save_bonus + situational_bonus
        
        return d20_roll, total, crit_success, crit_fail
    
    def calculate_spell_save_dc(self, spell_ability: str) -> int:
        """Рассчитывает Сложность спасброска заклинания.
        
        Args:
            spell_ability: Характеристика заклинателя (intelligence, wisdom, charisma)
            
        Returns:
            Сложность спасброска (8 + мод. характеристики + бонус мастерства)
        """
        # Модификатор характеристики заклинателя
        ability_value = getattr(self, spell_ability).value
        ability_modifier = (ability_value - 10) // 2
        
        # СЛ = 8 + модификатор характеристики + бонус мастерства
        save_dc = 8 + ability_modifier + self.get_proficiency_bonus()
        
        return save_dc
    
    def make_target_save(self, target_character, spell_ability: str, advantage: str = "none") -> tuple:
        """Заставляет цель совершить спасбросок от заклинания.
        
        Args:
            target_character: Цель спасброска
            spell_ability: Характеристика заклинателя
            advantage: Преимущество/помеха для цели
            
        Returns:
            Кортеж (СЛ_заклинания, бросок_цели, успех_спасброска)
        """
        save_dc = self.calculate_spell_save_dc(spell_ability)
        
        # Определяем характеристику для спасброска (зависит от заклинания)
        # TODO: Добавить определение характеристики спасброска от типа заклинания
        save_attribute = "wisdom"  # По умолчанию
        
        d20_roll, total, crit_success, crit_fail = target_character.roll_saving_throw(
            save_attribute, advantage
        )
        
        save_success = total >= save_dc
        
        return save_dc, total, save_success
    
    def get_all_skill_bonuses(self) -> Dict[str, int]:
        """Возвращает словарь всех бонусов навыков."""
        return {name: self.get_skill_bonus(name) for name in self.skills.keys()}
    
    def get_all_save_bonuses(self) -> Dict[str, int]:
        """Возвращает словарь всех бонусов спасбросков."""
        attributes = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']
        return {attr: self.get_saving_throw_bonus(attr) for attr in attributes}