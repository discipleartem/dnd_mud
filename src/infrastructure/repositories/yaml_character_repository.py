"""YAML репозиторий персонажей согласно Clean Architecture.

Реализует Repository Pattern для работы с YAML файлами,
изолируя бизнес-логику от инфраструктуры.
"""

from pathlib import Path
from typing import Any

from src.core.yaml_utils import load_yaml_file, save_yaml_file
from src.domain.entities.character import Character
from src.interfaces.repositories import ICharacterRepository


class YamlCharacterRepository(ICharacterRepository):
    """YAML репозиторий персонажей.

    Infrastructure слой - реализует доступ к данным
    через YAML файлы следуя Clean Architecture.
    """

    def __init__(
        self, data_dir: str = "data", characters_file: str = "characters.yaml"
    ) -> None:
        """Инициализировать репозиторий.

        Args:
            data_dir: Директория с YAML файлами
            characters_file: Имя файла с персонажами
        """
        self._data_dir = Path(data_dir)
        self._characters_file = characters_file
        self._characters: dict[str, Character] = {}
        self._load_data()

    def _load_data(self) -> None:
        """Загрузить данные из YAML файлов."""
        try:
            characters_data = load_yaml_file(
                self._data_dir / self._characters_file
            )
            for char_id, char_data in characters_data.items():
                character = self._create_character(char_id, char_data)
                self._characters[character.name] = character

        except FileNotFoundError as e:
            print(f"⚠️ Файл персонажей не найден: {e.filename}")

    def _create_character(
        self, char_id: str, char_data: dict[str, Any]
    ) -> Character:
        """Создать доменного персонажа из YAML данных.

        Args:
            char_id: ID персонажа
            char_data: Данные персонажа из YAML

        Returns:
            Доменная сущность Character
        """
        # Заглушка - в реальной реализации здесь была бы
        # полная десериализация из YAML с восстановлением
        # всех зависимостей (раса, характеристики и т.д.)

        return Character(
            name=char_data.get("name", char_id),
            race=None,  # Будет восстановлено из ID
            character_class=char_data.get("character_class", ""),
            level=char_data.get("level", 1),
            subrace=None,  # Будет восстановлено из ID
            sub_class=char_data.get("sub_class"),
            ability_scores=None,  # Будет восстановлено из данных
        )

    def save(self, entity: Character) -> Character:
        """Сохранить персонажа в YAML файл.

        Args:
            entity: Персонаж для сохранения

        Returns:
            Сохраненный персонаж
        """
        try:
            # Собираем данные для сохранения
            char_data = {
                "name": entity.name,
                "character_class": entity.character_class,
                "level": entity.level,
                "sub_class": entity.sub_class,
            }

            # Добавляем расу если есть
            if entity.race:
                char_data["race"] = entity.race.name
                if entity.subrace:
                    char_data["subrace"] = entity.subrace.name

            # Добавляем характеристики если есть
            if entity.ability_scores:
                char_data["ability_scores"] = entity.ability_scores.to_dict()

            # Добавляем языки если есть
            if entity.languages:
                char_data["languages"] = entity.languages

            # Сохраняем в YAML
            save_yaml_file(
                self._data_dir / self._characters_file,
                {entity.name: char_data},
            )

            # Обновляем кэш
            self._characters[entity.name] = entity

            print(f"💾 Персонаж {entity.name} сохранен")
            return entity

        except Exception as e:
            print(f"❌ Ошибка при сохранении персонажа: {e}")
            raise

    def find_by_name(self, name: str) -> Character | None:
        """Найти персонажа по имени.

        Args:
            name: Имя персонажа

        Returns:
            Персонаж или None если не найден
        """
        return self._characters.get(name)

    def find_by_race(self, race_name: str) -> list[Character]:
        """Найти персонажей расы.

        Args:
            race_name: Название расы

        Returns:
            Список персонажей указанной расы
        """
        return [
            char
            for char in self._characters.values()
            if char.race and char.race.name == race_name
        ]

    def find_by_id(self, entity_id: str) -> Character | None:
        """Найти персонажа по ID.

        Args:
            entity_id: ID персонажа

        Returns:
            Персонаж или None если не найден
        """
        # В текущей реализации ID совпадает с именем
        return self.find_by_name(entity_id)

    def find_all(self) -> list[Character]:
        """Получить всех персонажей.

        Returns:
            Список всех персонажей
        """
        return list(self._characters.values())

    def get_by_race(self, race_name: str) -> list[Character]:
        """Получить персонажей расы.

        Args:
            race_name: Название расы

        Returns:
            Список персонажей указанной расы
        """
        return self.find_by_race(race_name)

    def delete(self, entity_id: str) -> bool:
        """Удалить персонажа.

        Args:
            entity_id: ID персонажа для удаления

        Returns:
            True если удален
        """
        # Находим персонажа
        character = self._characters.get(entity_id)
        if not character:
            return False

        # Удаляем из кэша
        del self._characters[character.name]

        # В реальной реализации здесь было бы удаление из YAML файла
        print(f"🗑️ Персонаж {character.name} удален (заглушка)")
        return True
