"""Контроллер сохранений игр.

Следует Clean Architecture - преобразует данные между слоями.
Управляет операциями с сохранениями игр.
"""

from typing import Any

from src.dto.save_game_dto import (
    CharacterPreviewDTO,
    SaveGameDTO,
    SaveGameRequest,
    SaveGameResponse,
    SaveSlotDTO,
)
from src.interfaces.repositories.save_game_repository import RepositoryError
from src.use_cases.save_game_use_case import SaveGameUseCase


class SaveGameController:
    """Контроллер сохранений игр.

    Следует Clean Architecture - управляет операциями
    с сохранениями, преобразуя запросы в ответы.
    """

    def __init__(self, save_use_case: SaveGameUseCase) -> None:
        """Инициализация контроллера.

        Args:
            save_use_case: Use Case сохранений
        """
        self._save_use_case = save_use_case

    def handle_request(self, request: SaveGameRequest) -> SaveGameResponse:
        """Обработать запрос на операцию с сохранением.

        Args:
            request: Запрос на операцию

        Returns:
            Ответ контроллера с результатом операции
        """
        try:
            if request.action == "save":
                return self._handle_save(request)
            elif request.action == "load":
                return self._handle_load(request)
            elif request.action == "delete":
                return self._handle_delete(request)
            elif request.action == "list":
                return self._handle_list()
            elif request.action == "get_available_slots":
                return self._handle_get_available_slots()
            else:
                return SaveGameResponse(
                    success=False,
                    message=f"Неизвестное действие: {request.action}",
                )

        except ValueError as e:
            return SaveGameResponse(
                success=False, message=f"Ошибка валидации: {str(e)}"
            )
        except RepositoryError as e:
            return SaveGameResponse(
                success=False, message=f"Ошибка репозитория: {str(e)}"
            )
        except Exception as e:
            return SaveGameResponse(
                success=False, message=f"Внутренняя ошибка: {str(e)}"
            )

    def _handle_save(self, request: SaveGameRequest) -> SaveGameResponse:
        """Обработать сохранение игры.

        Args:
            request: Запрос на сохранение

        Returns:
            Ответ с результатом сохранения
        """
        if not all(
            [
                request.character_name,
                request.character_level is not None,
                request.character_class,
                request.character_data,
            ]
        ):
            return SaveGameResponse(
                success=False,
                message="Отсутствуют обязательные данные для сохранения",
            )

        try:
            save_game = self._save_use_case.create_new_save(
                character_name=request.character_name or "",
                character_level=request.character_level or 1,
                character_class=request.character_class or "",
                character_data=request.character_data or {},
                slot_number=request.slot_number or 1,
                location=request.location or "Начало пути",
            )

            # Преобразование даты в строку (универсальный подход)
            save_time_raw = save_game.save_time
            try:
                # Если это datetime, преобразуем в строку
                save_time_str = save_time_raw.strftime("%Y-%m-%d %H:%M:%S")
            except AttributeError:
                # Если это уже строка, используем как есть
                save_time_str = str(save_time_raw)

            save_dto = SaveGameDTO(
                save_id=save_game.save_id,
                character_name=save_game.character_name,
                character_level=save_game.character_level,
                character_class=save_game.character_class,
                save_time=save_time_str,
                slot_number=save_game.slot_number,
                game_version=save_game.game_version,
                playtime_minutes=save_game.playtime_minutes,
                location=save_game.location,
            )

            return SaveGameResponse(
                success=True,
                message="Игра успешно сохранена",
                save_game=save_dto.to_dict(),
            )

        except Exception as e:
            return SaveGameResponse(
                success=False, message=f"Ошибка сохранения: {str(e)}"
            )

    def _handle_load(self, request: SaveGameRequest) -> SaveGameResponse:
        """Обработать загрузку игры.

        Args:
            request: Запрос на загрузку

        Returns:
            Ответ с загруженными данными
        """
        if not request.save_id:
            return SaveGameResponse(
                success=False, message="Отсутствует ID сохранения"
            )

        try:
            game_data = self._save_use_case.load_game(request.save_id)

            if game_data is None:
                return SaveGameResponse(
                    success=False, message="Сохранение не найдено"
                )

            # Получаем метаданные сохранения
            save_game = self._save_use_case.get_save_by_id(request.save_id)

            # Создаем DTO из объекта SaveGame
            if save_game:
                # Преобразование даты в строку (универсальный подход)
                save_time_raw = save_game.save_time
                try:
                    # Если это datetime, преобразуем в строку
                    save_time_str = save_time_raw.strftime("%Y-%m-%d %H:%M:%S")
                except AttributeError:
                    # Если это уже строка, используем как есть
                    save_time_str = str(save_time_raw)

                save_dto = SaveGameDTO(
                    save_id=save_game.save_id,
                    character_name=save_game.character_name,
                    character_level=save_game.character_level,
                    character_class=save_game.character_class,
                    save_time=save_time_str,
                    slot_number=save_game.slot_number,
                    game_version=save_game.game_version,
                    playtime_minutes=save_game.playtime_minutes,
                    location=save_game.location,
                )
            else:
                save_dto = None

            return SaveGameResponse(
                success=True,
                message="Игра успешно загружена",
                game_data=game_data,
                save_game=save_dto.to_dict() if save_dto else None,
            )

        except Exception as e:
            return SaveGameResponse(
                success=False, message=f"Ошибка загрузки: {str(e)}"
            )

    def _handle_delete(self, request: SaveGameRequest) -> SaveGameResponse:
        """Обработать удаление сохранения.

        Args:
            request: Запрос на удаление

        Returns:
            Ответ с результатом удаления
        """
        if not request.save_id:
            return SaveGameResponse(
                success=False, message="Отсутствует ID сохранения"
            )

        try:
            deleted = self._save_use_case.delete_save(request.save_id)

            if deleted:
                return SaveGameResponse(
                    success=True, message="Сохранение успешно удалено"
                )
            else:
                return SaveGameResponse(
                    success=False,
                    message="Сохранение не найдено или не удалось удалить",
                )

        except Exception as e:
            return SaveGameResponse(
                success=False, message=f"Ошибка удаления: {str(e)}"
            )

    def _handle_list(self) -> SaveGameResponse:
        """Обработать запрос списка сохранений.

        Returns:
            Ответ со списком сохранений
        """
        try:
            saves = self._save_use_case.get_all_saves()

            saves_list = []
            for save in saves:
                save_dto = SaveGameDTO.from_entity(save)
                saves_list.append(save_dto.to_dict())

            return SaveGameResponse(
                success=True,
                message=f"Найдено сохранений: {len(saves_list)}",
                all_saves=saves_list,
            )

        except Exception as e:
            return SaveGameResponse(
                success=False, message=f"Ошибка получения списка: {str(e)}"
            )

    def _handle_get_available_slots(self) -> SaveGameResponse:
        """Обработать запрос доступных слотов.

        Returns:
            Ответ со списком доступных слотов
        """
        try:
            available_slots = self._save_use_case.get_available_slots()

            return SaveGameResponse(
                success=True,
                message="Список доступных слотов получен",
                available_slots=available_slots,
            )

        except Exception as e:
            return SaveGameResponse(
                success=False, message=f"Ошибка получения слотов: {str(e)}"
            )

    def get_save_slots_info(self) -> list[SaveSlotDTO]:
        """Получить информацию о всех слотах сохранения.

        Returns:
            Список слотов с информацией о сохранениях
        """
        try:
            saves = self._save_use_case.get_all_saves()
            used_slots = {save.slot_number: save for save in saves}

            slots = []
            for slot_num in range(1, 11):  # Слоты 1-10
                if slot_num in used_slots:
                    save = used_slots[slot_num]
                    # Преобразование даты в строку (универсальный подход)
                    save_time_raw = save.save_time
                    try:
                        # Если это datetime, преобразуем в строку
                        save_time_str = save_time_raw.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                    except AttributeError:
                        # Если это уже строка, используем как есть
                        save_time_str = str(save_time_raw)

                    save_dto = SaveGameDTO(
                        save_id=save.save_id,
                        character_name=save.character_name,
                        character_level=save.character_level,
                        character_class=save.character_class,
                        save_time=save_time_str,
                        slot_number=save.slot_number,
                        game_version=save.game_version,
                        playtime_minutes=save.playtime_minutes,
                        location=save.location,
                    )
                    slot_info = SaveSlotDTO(
                        slot_number=slot_num,
                        is_occupied=True,
                        save_info=save_dto,
                    )
                else:
                    slot_info = SaveSlotDTO(
                        slot_number=slot_num, is_occupied=False
                    )

                slots.append(slot_info)

            return slots

        except Exception as e:
            raise RepositoryError(
                f"Ошибка получения информации о слотах: {e}"
            ) from e

    def get_character_preview(
        self, save_id: str
    ) -> CharacterPreviewDTO | None:
        """Получить предпросмотр персонажа.

        Args:
            save_id: ID сохранения

        Returns:
            DTO предпросмотра персонажа или None
        """
        try:
            game_data = self._save_use_case.load_game(save_id)
            if not game_data:
                return None

            character_data = game_data.get("character", {})

            return CharacterPreviewDTO(
                name=character_data.get("name", "Неизвестный"),
                level=character_data.get("level", 1),
                character_class=character_data.get("class", "Неизвестный"),
                race=character_data.get("race"),
                background=character_data.get("background"),
                abilities=character_data.get("abilities"),
                hp=character_data.get("hp"),
                ac=character_data.get("ac"),
            )

        except Exception as e:
            raise RepositoryError(
                f"Ошибка получения предпросмотра: {e}"
            ) from e

    def quick_save(
        self,
        character_name: str,
        character_level: int,
        character_class: str,
        character_data: dict[str, Any],
        location: str = "Начало пути",
    ) -> SaveGameResponse:
        """Быстрое сохранение.

        Args:
            character_name: Имя персонажа
            character_level: Уровень персонажа
            character_class: Класс персонажа
            character_data: Данные персонажа
            location: Локация

        Returns:
            Ответ с результатом сохранения
        """
        try:
            save_game = self._save_use_case.quick_save(
                character_name=character_name,
                character_level=character_level,
                character_class=character_class,
                character_data=character_data,
                location=location,
            )

            # Преобразование даты в строку (универсальный подход)
            save_time_raw = save_game.save_time
            try:
                # Если это datetime, преобразуем в строку
                save_time_str = save_time_raw.strftime("%Y-%m-%d %H:%M:%S")
            except AttributeError:
                # Если это уже строка, используем как есть
                save_time_str = str(save_time_raw)

            save_dto = SaveGameDTO(
                save_id=save_game.save_id,
                character_name=save_game.character_name,
                character_level=save_game.character_level,
                character_class=save_game.character_class,
                save_time=save_time_str,
                slot_number=save_game.slot_number,
                game_version=save_game.game_version,
                playtime_minutes=save_game.playtime_minutes,
                location=save_game.location,
            )

            return SaveGameResponse(
                success=True,
                message=f"Игра быстро сохранена в слот {save_game.slot_number}",
                save_game=save_dto.to_dict(),
            )

        except Exception as e:
            return SaveGameResponse(
                success=False, message=f"Ошибка быстрого сохранения: {str(e)}"
            )
