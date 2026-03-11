"""Файловая реализация репозитория сохранений игр.

Следует Clean Architecture - конкретная реализация в слое Frameworks.
Работает с JSON файлами для хранения сохранений.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from src.interfaces.repositories.save_game_repository import (
    RepositoryError,
    SaveGame,
    SaveGameRepository,
)


class FileSaveGameRepository(SaveGameRepository):
    """Файловая реализация репозитория сохранений.

    Хранит сохранения в JSON файлах в директории saves/.
    """

    def __init__(self, saves_directory: str = "saves") -> None:
        """Инициализация репозитория.

        Args:
            saves_directory: Директория для сохранений
        """
        self._saves_directory = Path(saves_directory)
        self._saves_directory.mkdir(exist_ok=True)
        self._metadata_file = self._saves_directory / "metadata.json"

        # Создаем файл метаданных если не существует
        if not self._metadata_file.exists():
            self._create_metadata_file()

    def _create_metadata_file(self) -> None:
        """Создать файл метаданных."""
        try:
            with open(self._metadata_file, "w", encoding="utf-8") as f:
                json.dump({"saves": []}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise RepositoryError(
                f"Ошибка создания файла метаданных: {e}"
            ) from e

    def _load_metadata(self) -> dict[str, Any]:
        """Загрузить метаданные.

        Returns:
            Словарь с метаданными

        Raises:
            RepositoryError: Ошибка загрузки
        """
        try:
            with open(self._metadata_file, encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise RepositoryError(
                f"Ошибка чтения файла метаданных: {e}"
            ) from e
        except Exception as e:
            raise RepositoryError(f"Ошибка загрузки метаданных: {e}") from e

    def _save_metadata(self, metadata: dict[str, Any]) -> None:
        """Сохранить метаданные.

        Args:
            metadata: Метаданные для сохранения

        Raises:
            RepositoryError: Ошибка сохранения
        """
        try:
            with open(self._metadata_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise RepositoryError(f"Ошибка сохранения метаданных: {e}") from e

    def _get_save_file_path(self, save_id: str) -> Path:
        """Получить путь к файлу сохранения.

        Args:
            save_id: ID сохранения

        Returns:
            Путь к файлу сохранения
        """
        return self._saves_directory / f"{save_id}.json"

    def save(self, save_game: SaveGame, game_data: dict[str, Any]) -> SaveGame:
        """Сохранить игру.

        Args:
            save_game: Метаданные сохранения
            game_data: Полные данные игры для сохранения

        Returns:
            Сохранённая игра с ID

        Raises:
            RepositoryError: Ошибка сохранения
        """
        try:
            # Валидация формата
            if not self.validate_save_format(game_data):
                raise RepositoryError("Неверный формат данных сохранения")

            # Загружаем метаданные
            metadata = self._load_metadata()

            # Проверяем, не занят ли слот
            existing_saves = [
                s
                for s in metadata["saves"]
                if s["slot_number"] == save_game.slot_number
                and s["save_id"] != save_game.save_id
            ]

            if existing_saves:
                # Удаляем старое сохранение из этого слота
                old_save_id = existing_saves[0]["save_id"]
                self.delete(old_save_id)
                metadata = (
                    self._load_metadata()
                )  # Перезагружаем после удаления

            # Сохраняем данные игры
            save_file_path = self._get_save_file_path(save_game.save_id)
            save_data = {
                "metadata": save_game.to_dict(),
                "game_data": game_data,
                "saved_at": datetime.now().isoformat(),
            }

            with open(save_file_path, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)

            # Обновляем метаданные
            save_dict = save_game.to_dict()

            # Удаляем старую запись если есть
            metadata["saves"] = [
                s
                for s in metadata["saves"]
                if s["save_id"] != save_game.save_id
            ]

            # Добавляем новую запись
            metadata["saves"].append(save_dict)

            # Сортируем по времени сохранения (новые первые)
            metadata["saves"].sort(key=lambda x: x["save_time"], reverse=True)

            self._save_metadata(metadata)

            return save_game

        except Exception as e:
            if isinstance(e, RepositoryError):
                raise
            raise RepositoryError(f"Ошибка сохранения игры: {e}") from e

    def load(self, save_id: str) -> dict[str, Any] | None:
        """Загрузить игру.

        Args:
            save_id: ID сохранения

        Returns:
            Данные игры или None если не найдено

        Raises:
            RepositoryError: Ошибка загрузки
        """
        try:
            save_file_path = self._get_save_file_path(save_id)

            if not save_file_path.exists():
                return None

            with open(save_file_path, encoding="utf-8") as f:
                save_data = json.load(f)

            return save_data.get("game_data")

        except json.JSONDecodeError as e:
            raise RepositoryError(
                f"Ошибка чтения файла сохранения: {e}"
            ) from e
        except Exception as e:
            if isinstance(e, RepositoryError):
                raise
            raise RepositoryError(f"Ошибка загрузки игры: {e}") from e

    def find_by_id(self, save_id: str) -> SaveGame | None:
        """Найти сохранение по ID.

        Args:
            save_id: ID сохранения

        Returns:
            Сохранение или None если не найдено

        Raises:
            RepositoryError: Ошибка поиска
        """
        try:
            metadata = self._load_metadata()

            for save_dict in metadata["saves"]:
                if save_dict["save_id"] == save_id:
                    return SaveGame.from_dict(save_dict)

            return None

        except Exception as e:
            if isinstance(e, RepositoryError):
                raise
            raise RepositoryError(f"Ошибка поиска сохранения: {e}") from e

    def find_by_slot(self, slot_number: int) -> SaveGame | None:
        """Найти сохранение по номеру слота.

        Args:
            slot_number: Номер слота сохранения

        Returns:
            Сохранение или None если не найдено

        Raises:
            RepositoryError: Ошибка поиска
        """
        try:
            metadata = self._load_metadata()

            for save_dict in metadata["saves"]:
                if save_dict["slot_number"] == slot_number:
                    return SaveGame.from_dict(save_dict)

            return None

        except Exception as e:
            if isinstance(e, RepositoryError):
                raise
            raise RepositoryError(f"Ошибка поиска сохранения: {e}") from e

    def find_all(self) -> list[SaveGame]:
        """Получить все сохранения.

        Returns:
            Список всех сохранений

        Raises:
            RepositoryError: Ошибка получения
        """
        try:
            metadata = self._load_metadata()

            saves = []
            for save_dict in metadata["saves"]:
                saves.append(SaveGame.from_dict(save_dict))

            return saves

        except Exception as e:
            if isinstance(e, RepositoryError):
                raise
            raise RepositoryError(f"Ошибка получения сохранений: {e}") from e

    def delete(self, save_id: str) -> bool:
        """Удалить сохранение.

        Args:
            save_id: ID сохранения

        Returns:
            True если удалено успешно

        Raises:
            RepositoryError: Ошибка удаления
        """
        try:
            # Удаляем файл сохранения
            save_file_path = self._get_save_file_path(save_id)
            file_deleted = False

            if save_file_path.exists():
                save_file_path.unlink()
                file_deleted = True

            # Удаляем из метаданных
            metadata = self._load_metadata()
            original_count = len(metadata["saves"])

            metadata["saves"] = [
                s for s in metadata["saves"] if s["save_id"] != save_id
            ]

            metadata_deleted = len(metadata["saves"]) < original_count

            if metadata_deleted:
                self._save_metadata(metadata)

            return file_deleted or metadata_deleted

        except Exception as e:
            if isinstance(e, RepositoryError):
                raise
            raise RepositoryError(f"Ошибка удаления сохранения: {e}") from e

    def validate_save_format(self, game_data: dict[str, Any]) -> bool:
        """Валидировать формат сохранения.

        Args:
            game_data: Данные игры для валидации

        Returns:
            True если формат корректен
        """
        try:
            # Проверяем обязательные поля
            required_fields = ["character", "game_state", "version"]
            for field in required_fields:
                if field not in game_data:
                    return False

            # Проверяем структуру персонажа
            character = game_data["character"]
            if not isinstance(character, dict):
                return False

            character_required = ["name", "level", "class", "abilities"]
            for field in character_required:
                if field not in character:
                    return False

            # Проверяем структуру состояния игры
            game_state = game_data["game_state"]
            if not isinstance(game_state, dict):
                return False

            return True

        except Exception:
            return False
