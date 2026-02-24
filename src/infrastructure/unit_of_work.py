"""Unit of Work Pattern для управления транзакциями.

Реализует паттерн Unit of Work для атомарных операций
с несколькими репозиториями согласно Clean Architecture.
"""

from typing import Any

from src.interfaces.repositories import (
    ICharacterRepository,
    ILanguageRepository,
    IRaceRepository,
)


class UnitOfWork:
    """Unit of Work для управления транзакциями.

    Обеспечивает атомарность операций с несколькими
    репозиториями и отслеживание изменений.
    """

    def __init__(
        self,
        race_repository: IRaceRepository,
        language_repository: ILanguageRepository,
        character_repository: ICharacterRepository,
    ) -> None:
        """Инициализировать Unit of Work.

        Args:
            race_repository: Репозиторий рас
            language_repository: Репозиторий языков
            character_repository: Репозиторий персонажей
        """
        self._race_repository = race_repository
        self._language_repository = language_repository
        self._character_repository = character_repository

        # Отслеживание изменений
        self._new_entities: dict[str, Any] = {}
        self._modified_entities: dict[str, Any] = {}
        self._deleted_entities: dict[str, Any] = {}

        # Флаг транзакции
        self._in_transaction = False

    @property
    def races(self) -> IRaceRepository:
        """Репозиторий рас."""
        return self._race_repository

    @property
    def languages(self) -> ILanguageRepository:
        """Репозиторий языков."""
        return self._language_repository

    @property
    def characters(self) -> ICharacterRepository:
        """Репозиторий персонажей."""
        return self._character_repository

    def begin_transaction(self) -> None:
        """Начать транзакцию."""
        if self._in_transaction:
            raise RuntimeError("Транзакция уже активна")

        self._in_transaction = True
        self._new_entities.clear()
        self._modified_entities.clear()
        self._deleted_entities.clear()

    def commit(self) -> None:
        """Завершить транзакцию."""
        if not self._in_transaction:
            raise RuntimeError("Нет активной транзакции")

        try:
            # Сохраняем новые сущности
            for entity_type, entities in self._new_entities.items():
                for entity in entities.values():
                    self._save_entity(entity_type, entity)

            # Сохраняем измененные сущности
            for entity_type, entities in self._modified_entities.items():
                for entity in entities.values():
                    self._save_entity(entity_type, entity)

            # Удаляем сущности
            for entity_type, entities in self._deleted_entities.items():
                for entity_id in entities:
                    self._delete_entity(entity_type, entity_id)

            self._in_transaction = False
            self._clear_tracking()

        except Exception:
            self.rollback()
            raise

    def rollback(self) -> None:
        """Откатить транзакцию."""
        if not self._in_transaction:
            return

        self._in_transaction = False
        self._clear_tracking()

    def _save_entity(self, entity_type: str, entity: Any) -> None:
        """Сохранить сущность в соответствующий репозиторий."""
        if entity_type == "race":
            self._race_repository.save(entity)
        elif entity_type == "language":
            self._language_repository.save(entity)
        elif entity_type == "character":
            self._character_repository.save(entity)
        else:
            raise ValueError(f"Неизвестный тип сущности: {entity_type}")

    def _delete_entity(self, entity_type: str, entity_id: str) -> None:
        """Удалить сущность из соответствующего репозитория."""
        if entity_type == "race":
            self._race_repository.delete(entity_id)
        elif entity_type == "language":
            self._language_repository.delete(entity_id)
        elif entity_type == "character":
            self._character_repository.delete(entity_id)
        else:
            raise ValueError(f"Неизвестный тип сущности: {entity_type}")

    def _clear_tracking(self) -> None:
        """Очистить отслеживание изменений."""
        self._new_entities.clear()
        self._modified_entities.clear()
        self._deleted_entities.clear()

    def register_new(self, entity_type: str, entity: Any) -> None:
        """Зарегистрировать новую сущность."""
        if not self._in_transaction:
            return

        if entity_type not in self._new_entities:
            self._new_entities[entity_type] = {}

        entity_id = getattr(
            entity, "name", getattr(entity, "code", str(id(entity)))
        )
        self._new_entities[entity_type][entity_id] = entity

    def register_modified(self, entity_type: str, entity: Any) -> None:
        """Зарегистрировать измененную сущность."""
        if not self._in_transaction:
            return

        if entity_type not in self._modified_entities:
            self._modified_entities[entity_type] = {}

        entity_id = getattr(
            entity, "name", getattr(entity, "code", str(id(entity)))
        )
        self._modified_entities[entity_type][entity_id] = entity

    def register_deleted(self, entity_type: str, entity_id: str) -> None:
        """Зарегистрировать удаленную сущность."""
        if not self._in_transaction:
            return

        if entity_type not in self._deleted_entities:
            self._deleted_entities[entity_type] = []

        self._deleted_entities[entity_type].append(entity_id)

    def __enter__(self) -> "UnitOfWork":
        """Контекстный менеджер - вход."""
        self.begin_transaction()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Контекстный менеджер - выход."""
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
