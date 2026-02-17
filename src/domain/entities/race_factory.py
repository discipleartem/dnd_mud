# src/core/entities/race_factory.py
import yaml
import os
from typing import Dict, List, Optional
from .race import Race


class RaceFactory:
    """Фабрика для создания рас из YAML конфигурации."""

    _races_cache: Dict[str, Race] = {}
    _races_data: Dict = {}

    @classmethod
    def _load_races_data(cls) -> Dict:
        """Загружает данные о расах из YAML файла."""
        if not cls._races_data:
            # Определяем путь к файлу с данными о расах
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            races_file = os.path.join(project_root, 'data', 'yaml', 'races', 'races.yaml')
            
            try:
                with open(races_file, 'r', encoding='utf-8') as file:
                    cls._races_data = yaml.safe_load(file) or {}
            except FileNotFoundError:
                print(f"Предупреждение: Файл с расами не найден: {races_file}")
                cls._races_data = {}
        
        return cls._races_data

    @classmethod
    def get_race_key_by_name(cls, race_name: str) -> Optional[str]:
        """Возвращает ключ расы по локализованному имени."""
        races_data = cls._load_races_data()
        
        for race_key, race_data in races_data.items():
            if race_data["name"] == race_name:
                return race_key
            # Проверяем также подрасы
            if "subraces" in race_data:
                for sub_key, sub_data in race_data["subraces"].items():
                    if sub_data["name"] == race_name:
                        return f"{race_key}.{sub_key}"
        
        return None

    @classmethod
    def create_race(cls, race_key: str, subrace_key: Optional[str] = None) -> Race:
        """Создает объект расы по ключу.

        Args:
            race_key: Ключ расы (human, elf, half_orc)
            subrace_key: Ключ подрасы (high_elf, wood_elf)

        Returns:
            Объект расы
        """
        cache_key = f"{race_key}_{subrace_key}" if subrace_key else race_key

        if cache_key in cls._races_cache:
            return cls._races_cache[cache_key]

        races_data = cls._load_races_data()

        if race_key not in races_data:
            raise ValueError(f"Раса '{race_key}' не найдена")

        race_data = races_data[race_key]

        # Если запрошена подраса
        if (
            subrace_key
            and "subraces" in race_data
            and subrace_key in race_data["subraces"]
        ):
            subrace_data = race_data["subraces"][subrace_key]
            race = Race(
                name=subrace_data["name"],
                bonuses=subrace_data.get("bonuses", {}),
                description=subrace_data.get("description", ""),
                alternative_features=subrace_data.get("alternative_features", race_data.get("alternative_features", {})),
            )
        else:
            race = Race(
                name=race_data["name"],
                bonuses=race_data.get("bonuses", {}),
                description=race_data.get("description", ""),
                alternative_features=race_data.get("alternative_features", {}),
            )

        # Добавляем подрасы если они есть
        if "subraces" in race_data:
            for sub_key, sub_data in race_data["subraces"].items():
                subrace = Race(
                    name=sub_data["name"],
                    bonuses=sub_data.get("bonuses", {}),
                    description=sub_data.get("description", ""),
                    alternative_features=sub_data.get("alternative_features", {}),
                )
                # Используем sub_key как ключ, а не локализованное имя
                race.subraces[sub_key] = subrace

        cls._races_cache[cache_key] = race
        return race

    @classmethod
    def get_all_races(cls) -> List[Race]:
        """Возвращает список всех доступных рас."""
        races_data = cls._load_races_data()
        races = []

        for race_key in races_data:
            races.append(cls.create_race(race_key))

        return races

    @classmethod
    def get_race_choices(cls) -> Dict[str, str]:
        """Возвращает словарь для меню выбора основных рас."""
        races_data = cls._load_races_data()
        choices = {}
        choice_num = 1

        for race_key, race_data in races_data.items():
            choices[str(choice_num)] = race_data["name"]
            choice_num += 1

        return choices

    @classmethod
    def get_race_key_by_choice(cls, choice_num: int) -> Optional[str]:
        """Возвращает ключ расы по номеру выбора."""
        races_data = cls._load_races_data()
        race_keys = list(races_data.keys())

        if 1 <= choice_num <= len(race_keys):
            return race_keys[choice_num - 1]

        return None

    @classmethod
    def get_subrace_choices(cls, race_key: str) -> Dict[str, str]:
        """Возвращает словарь для меню выбора подрас указанной расы."""
        races_data = cls._load_races_data()

        if race_key not in races_data:
            return {}

        race_data = races_data[race_key]
        choices = {}
        choice_num = 1

        # Добавляем основную расу как вариант
        choices[str(choice_num)] = race_data["name"]
        choice_num += 1

        # Добавляем подрасы если они есть
        if "subraces" in race_data and race_data["subraces"]:
            for sub_key, sub_data in race_data["subraces"].items():
                choices[str(choice_num)] = sub_data["name"]
                choice_num += 1

        return choices

    @classmethod
    def get_subrace_key_by_choice(cls, race_key: str, choice_num: int) -> Optional[str]:
        """Возвращает ключ подрасы по номеру выбора."""
        races_data = cls._load_races_data()

        if race_key not in races_data:
            return None

        race_data = races_data[race_key]

        # choice_num == 1 означает основную расу (без подрасы)
        if choice_num == 1:
            return None

        # Для подрас
        if "subraces" in race_data and race_data["subraces"]:
            subrace_keys = list(race_data["subraces"].keys())
            subrace_index = (
                choice_num - 2
            )  # -1 для основной расы, -1 для индексации с 0

            if 0 <= subrace_index < len(subrace_keys):
                return subrace_keys[subrace_index]

        return None

    @classmethod
    def get_available_races(cls) -> List[Race]:
        """Возвращает список всех доступных рас."""
        return cls.get_all_races()

    @classmethod
    def clear_cache(cls) -> None:
        """Очищает кэш рас."""
        cls._races_cache.clear()
