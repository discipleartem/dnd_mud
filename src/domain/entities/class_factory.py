# src/domain/entities/class_factory.py
from typing import Dict, List, Optional, TypedDict, Union
from .class_ import CharacterClass


class ClassData(TypedDict):
    """Данные класса."""

    name: str
    description: Optional[str]
    hit_die: Optional[str]
    primary_ability: Optional[str]
    saving_throws: Optional[List[str]]
    armor_proficiencies: Optional[List[str]]
    weapon_proficiencies: Optional[List[str]]
    level: Optional[int]
    spellcasting: Optional[
        Dict[str, Union[str, int, List[str], Dict[str, Union[str, int]]]]
    ]
    divine_domain: Optional[str]
    skills: Optional[Dict[str, Union[str, int, bool]]]
    subclasses: Optional[List[Dict[str, Union[str, int]]]]
    features: Optional[List[Dict[str, Union[str, int, bool]]]]


class ClassesConfig(TypedDict):
    """Конфигурация классов."""

    classes: Dict[str, ClassData]


class CharacterClassFactory:
    """Фабрика для создания классов из YAML конфигурации."""

    _classes_cache: Dict[str, CharacterClass] = {}

    @classmethod
    def get_class_key_by_name(cls, class_name: str) -> Optional[str]:
        """Возвращает ключ класса по локализованному имени."""
        classes_data = cls.get_all_classes_data()

        for class_key, class_data in classes_data.items():
            if class_data["name"] == class_name:
                return class_key

        return None

    @classmethod
    def create_class(cls, class_key: str) -> CharacterClass:
        """Создает объект класса по ключу.

        Args:
            class_key: Ключ класса (fighter, rogue, bard, cleric)

        Returns:
            Объект класса
        """
        if class_key in cls._classes_cache:
            return cls._classes_cache[class_key]

        classes_data = cls.get_all_classes_data()

        if class_key not in classes_data:
            raise ValueError(f"Класс '{class_key}' не найден")

        class_data = classes_data[class_key]

        character_class = CharacterClass(
            name=class_data["name"],
            description=class_data.get("description", "") or "",
            hit_die=class_data.get("hit_die", "d10") or "d10",
        )

        # Сохраняем дополнительные данные в атрибутах
        character_class.primary_ability = str(
            class_data.get("primary_ability", "strength")
        )

        saving_throws_data = class_data.get("saving_throws", [])
        character_class.saving_throws = (
            list(saving_throws_data) if saving_throws_data else []
        )

        armor_proficiencies_data = class_data.get("armor_proficiencies", [])
        character_class.armor_proficiencies = (
            list(armor_proficiencies_data) if armor_proficiencies_data else []
        )

        weapon_proficiencies_data = class_data.get("weapon_proficiencies", [])
        character_class.weapon_proficiencies = (
            list(weapon_proficiencies_data) if weapon_proficiencies_data else []
        )

        # Получаем данные заклинаний с правильной структурой
        spellcasting_data = class_data.get("spellcasting", {})
        if not isinstance(spellcasting_data, dict):
            spellcasting_data = {}

        # Извлекаем данные с безопасными значениями по умолчанию
        ability = str(spellcasting_data.get("ability", ""))
        spell_list_raw = spellcasting_data.get("spell_list", [])
        spell_list = (
            list(spell_list_raw) if isinstance(spell_list_raw, (list, tuple)) else []
        )
        cantrips_raw = spellcasting_data.get("cantrips", [])
        cantrips = list(cantrips_raw) if isinstance(cantrips_raw, (list, tuple)) else []
        spells_per_day_raw = spellcasting_data.get("spells_per_day", {})
        spells_per_day = (
            dict(spells_per_day_raw) if isinstance(spells_per_day_raw, dict) else {}
        )
        ritual_casting = (
            bool(spellcasting_data.get("ritual_casting", False))
            if isinstance(spellcasting_data.get("ritual_casting"), (bool, type(None)))
            else False
        )
        spell_ability = (
            str(spellcasting_data.get("spell_ability", ""))
            if isinstance(spellcasting_data.get("spell_ability"), (str, type(None)))
            else ""
        )
        prepared_spells = (
            bool(spellcasting_data.get("prepared_spells", False))
            if isinstance(spellcasting_data.get("prepared_spells"), (bool, type(None)))
            else False
        )
        known_spells = (
            spellcasting_data.get("known_spells")
            if isinstance(spellcasting_data.get("known_spells"), (list, type(None)))
            else None
        )
        extra_attacks = (
            spellcasting_data.get("extra_attacks")
            if isinstance(spellcasting_data.get("extra_attacks"), (list, type(None)))
            else None
        )

        spells_per_day_converted = {}
        for k, v in spells_per_day.items():
            if isinstance(v, int):
                spells_per_day_converted[k] = v
            elif isinstance(v, list) and all(isinstance(x, int) for x in v):
                spells_per_day_converted[k] = v
            else:
                # Пропускаем невалидные значения
                continue

        character_class.spellcasting = {
            "ability": ability,
            "spell_list": spell_list,
            "cantrips": cantrips,
            "spells_per_day": spells_per_day_converted,  # type: ignore
            "ritual_casting": ritual_casting,
            "spell_ability": spell_ability,
            "prepared_spells": prepared_spells,
            "known_spells": known_spells,  # type: ignore
            "extra_attacks": extra_attacks,  # type: ignore
        }

        character_class.divine_domain = class_data.get("divine_domain")
        skills_data = class_data.get("skills", {})
        character_class.skills = (
            dict(skills_data) if isinstance(skills_data, dict) else {}
        )

        cls._classes_cache[class_key] = character_class
        return character_class

    @classmethod
    def get_all_classes_data(cls) -> Dict[str, ClassData]:
        """Возвращает все данные классов из YAML."""
        try:
            path = (
                __import__("pathlib").Path(__file__).parent.parent.parent.parent
                / "data"
                / "yaml"
                / "attributes"
                / "core_classes.yaml"
            )
            with open(path, "r", encoding="utf-8") as file:
                import yaml

                data = yaml.safe_load(file) or {}
                classes_data = data.get("classes", {})
                # Преобразуем в ClassData
                result: Dict[str, ClassData] = {}
                for class_key, class_data in classes_data.items():
                    if isinstance(class_data, dict):
                        result[class_key] = {
                            "name": class_data.get("name", class_key),
                            "description": class_data.get("description"),
                            "hit_die": class_data.get("hit_die"),
                            "primary_ability": class_data.get("primary_ability"),
                            "saving_throws": class_data.get("saving_throws"),
                            "armor_proficiencies": class_data.get(
                                "armor_proficiencies"
                            ),
                            "weapon_proficiencies": class_data.get(
                                "weapon_proficiencies"
                            ),
                            "spellcasting": class_data.get("spellcasting"),
                            "divine_domain": class_data.get("divine_domain"),
                            "skills": class_data.get("skills"),
                            "level": class_data.get("level"),
                            "subclasses": class_data.get("subclasses"),
                            "features": class_data.get("features"),
                        }
                return result
        except FileNotFoundError:
            print("Файл классов не найден, возвращаем пустой словарь")
            return {}

    @classmethod
    def get_all_classes(cls) -> List[CharacterClass]:
        """Возвращает список всех доступных классов."""
        classes_data = cls.get_all_classes_data()
        classes = []

        for class_key in classes_data:
            classes.append(cls.create_class(class_key))

        return classes

    @classmethod
    def get_class_choices(cls) -> Dict[str, str]:
        """Возвращает словарь для меню выбора классов."""
        classes_data = cls.get_all_classes_data()
        choices = {}
        choice_num = 1

        for class_key, class_data in classes_data.items():
            choices[str(choice_num)] = class_data["name"]
            choice_num += 1

        return choices

    @classmethod
    def get_class_key_by_choice(cls, choice_num: int) -> Optional[str]:
        """Возвращает ключ класса по номеру выбора."""
        classes_data = cls.get_all_classes_data()
        class_keys = list(classes_data.keys())

        if 1 <= choice_num <= len(class_keys):
            return class_keys[choice_num - 1]

        return None

    @classmethod
    def find_class_by_name(cls, name: str) -> Optional[CharacterClass]:
        """Находит класс по названию."""
        for character_class in cls.get_all_classes():
            if character_class.name == name:
                return character_class
        return None

    @classmethod
    def get_available_classes(cls) -> List[CharacterClass]:
        """Возвращает список всех доступных классов."""
        return cls.get_all_classes()

    @classmethod
    def clear_cache(cls) -> None:
        """Очищает кэш классов."""
        cls._classes_cache.clear()
        pass
