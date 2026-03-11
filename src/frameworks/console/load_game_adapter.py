"""Консольный адаптер для загрузки игр.

Следует Clean Architecture - конкретная реализация в слое Frameworks.
Предоставляет консольный интерфейс для управления сохранениями.
"""

from src.dto.save_game_dto import CharacterPreviewDTO, SaveGameDTO, SaveSlotDTO


class LoadGameMenuAdapter:
    """Консольный адаптер меню загрузки игр.

    Следует Clean Architecture - предоставляет консольный интерфейс
    для работы с сохранениями игр.
    """

    def __init__(self, use_colors: bool = True) -> None:
        """Инициализация адаптера.

        Args:
            use_colors: Использовать цвета в выводе
        """
        self.use_colors = use_colors
        self._color_codes = {
            "reset": "\033[0m",
            "title": "\033[1;36m",  # Cyan bold
            "highlight": "\033[1;33m",  # Yellow bold
            "success": "\033[1;32m",  # Green bold
            "error": "\033[1;31m",  # Red bold
            "info": "\033[1;34m",  # Blue bold
            "dim": "\033[2m",  # Dim
        }

    def _colorize(self, text: str, color: str) -> str:
        """Раскрасить текст.

        Args:
            text: Текст для раскраски
            color: Цвет из _color_codes

        Returns:
            Раскрашенный текст или обычный если цвета отключены
        """
        if not self.use_colors:
            return text

        color_code = self._color_codes.get(color, "")
        reset_code = self._color_codes.get("reset", "")

        return f"{color_code}{text}{reset_code}"

    def display_load_menu(self, slots: list[SaveSlotDTO]) -> None:
        """Отобразить меню загрузки игр.

        Args:
            slots: Список слотов сохранения
        """
        print(f"\n{self._colorize('=' * 60, 'title')}")
        print(f"{self._colorize('ЗАГРУЗКА ИГРЫ', 'title')}")
        print(f"{self._colorize('=' * 60, 'title')}")
        print()

        if not slots:
            print(f"{self._colorize('Нет доступных сохранений', 'info')}")
            print()
            return

        # Группируем слоты по 5 для удобного отображения
        for i in range(0, len(slots), 5):
            batch = slots[i : i + 5]

            # Заголовки колонок
            print(
                f"{'Слот':<6} {'Персонаж':<20} {'Уровень':<8} {'Класс':<15} {'Время':<12}"
            )
            print("-" * 65)

            # Данные слотов
            for slot in batch:
                if slot.is_occupied and slot.save_info:
                    save_info = slot.save_info
                    print(
                        f"{self._colorize(str(slot.slot_number), 'highlight'):<6} "
                        f"{save_info.character_name[:19]:<20} "
                        f"{save_info.character_level:<8} "
                        f"{save_info.character_class[:14]:<15} "
                        f"{save_info.save_time[:11]:<12}"
                    )
                else:
                    print(
                        f"{self._colorize(str(slot.slot_number), 'dim'):<6} "
                        f"{self._colorize('Пустой слот', 'dim'):<20} "
                        f"{'-':<8} {'-':<15} {'-':<12}"
                    )

            if i + 5 < len(slots):
                print()  # Пустая строка между группами

        print()
        print(f"{self._colorize('0', 'highlight')}. Назад в главное меню")
        print()
        print(f"{self._colorize('-', 'dim')} * 30")

    def get_user_choice(self) -> str:
        """Получить выбор пользователя.

        Returns:
            Выбор пользователя
        """
        try:
            choice = input("Ваш выбор: ").strip()
            return choice
        except (KeyboardInterrupt, EOFError):
            return "0"

    def display_save_preview(
        self, save_info: SaveGameDTO, preview: CharacterPreviewDTO
    ) -> None:
        """Отобразить предпросмотр сохранения.

        Args:
            save_info: Информация о сохранении
            preview: Предпросмотр персонажа
        """
        print(f"\n{self._colorize('=' * 50, 'title')}")
        print(f"{self._colorize('ПРЕДПРОСМОТР СОХРАНЕНИЯ', 'title')}")
        print(f"{self._colorize('=' * 50, 'title')}")
        print()

        # Информация о сохранении
        print(f"{self._colorize('Информация о сохранении:', 'highlight')}")
        print(f"  Слот: {save_info.slot_number}")
        print(f"  Время сохранения: {save_info.save_time}")
        print(
            f"  Время игры: {save_info.playtime_minutes // 60}ч {save_info.playtime_minutes % 60}м"
        )
        print(f"  Локация: {save_info.location}")
        print(f"  Версия игры: {save_info.game_version}")
        print()

        # Информация о персонаже
        print(f"{self._colorize('Информация о персонаже:', 'highlight')}")
        print(f"  Имя: {preview.name}")
        print(f"  Уровень: {preview.level}")
        print(f"  Класс: {preview.character_class}")

        if preview.race:
            print(f"  Раса: {preview.race}")

        if preview.background:
            print(f"  Предыстория: {preview.background}")

        # Характеристики
        if preview.abilities:
            print(f"\n{self._colorize('Характеристики:', 'highlight')}")
            for ability, value in preview.abilities.items():
                modifier = (value - 10) // 2
                mod_str = f"+{modifier}" if modifier >= 0 else str(modifier)
                print(f"  {ability.capitalize()}: {value} ({mod_str})")

        # Боевая информация
        if preview.hp is not None or preview.ac is not None:
            print(f"\n{self._colorize('Боевая информация:', 'highlight')}")
            if preview.hp is not None:
                print(f"  Здоровье: {preview.hp}")
            if preview.ac is not None:
                print(f"  Класс доспеха: {preview.ac}")

        print()

    def confirm_load(self, save_info: SaveGameDTO) -> bool:
        """Подтвердить загрузку сохранения.

        Args:
            save_info: Информация о сохранении

        Returns:
            True если пользователь подтвердил загрузку
        """
        print(f"{self._colorize('Загрузить сохранение', 'info')}:")
        print(
            f"  {save_info.character_name} (уровень {save_info.character_level} {save_info.character_class})"
        )
        print(f"  Слот {save_info.slot_number} от {save_info.save_time}")
        print()

        while True:
            try:
                choice = (
                    input("Загрузить это сохранение? (да/нет): ")
                    .strip()
                    .lower()
                )

                if choice in ["да", "д", "yes", "y"]:
                    return True
                elif choice in ["нет", "н", "no", "n"]:
                    return False
                else:
                    print("Введите 'да' или 'нет'")

            except (KeyboardInterrupt, EOFError):
                return False

    def confirm_delete(self, save_info: SaveGameDTO) -> bool:
        """Подтвердить удаление сохранения.

        Args:
            save_info: Информация о сохранении

        Returns:
            True если пользователь подтвердил удаление
        """
        print(f"{self._colorize('ВНИМАНИЕ!', 'error')}")
        print("Вы собираетесь удалить сохранение:")
        print(
            f"  {save_info.character_name} (уровень {save_info.character_level} {save_info.character_class})"
        )
        print(f"  Слот {save_info.slot_number} от {save_info.save_time}")
        print(f"{self._colorize('Это действие нельзя отменить!', 'error')}")
        print()

        while True:
            try:
                choice = (
                    input("Удалить это сохранение? (да/нет): ").strip().lower()
                )

                if choice in ["да", "д", "yes", "y"]:
                    return True
                elif choice in ["нет", "н", "no", "n"]:
                    return False
                else:
                    print("Введите 'да' или 'нет'")

            except (KeyboardInterrupt, EOFError):
                return False

    def display_message(
        self, message: str, message_type: str = "info"
    ) -> None:
        """Отобразить сообщение.

        Args:
            message: Текст сообщения
            message_type: Тип сообщения (info, success, error)
        """
        color = message_type if message_type in self._color_codes else "info"
        print(f"{self._colorize(message, color)}")

    def display_error(self, error: str) -> None:
        """Отобразить ошибку.

        Args:
            error: Текст ошибки
        """
        print(f"{self._colorize(f'Ошибка: {error}', 'error')}")

    def display_success(self, message: str) -> None:
        """Отобразить успешное сообщение.

        Args:
            message: Текст сообщения
        """
        print(f"{self._colorize(f'✅ {message}', 'success')}")

    def wait_for_continue(self) -> None:
        """Ожидать нажатия Enter для продолжения."""
        try:
            input("\nНажмите Enter для продолжения...")
        except (KeyboardInterrupt, EOFError):
            print()

    def clear_screen(self) -> None:
        """Очистить экран."""
        print("\033[2J\033[H", end="")

    def show_no_saves_message(self) -> None:
        """Показать сообщение об отсутствии сохранений."""
        print(f"\n{self._colorize('Нет доступных сохранений', 'info')}")
        print("Создайте нового персонажа или сохраните игру")
        print("чтобы увидеть сохранения в этом меню.")
        self.wait_for_continue()

    def show_slot_empty_message(self, slot_number: int) -> None:
        """Показать сообщение о пустом слоте.

        Args:
            slot_number: Номер пустого слота
        """
        print(f"\n{self._colorize(f'Слот {slot_number} пуст', 'info')}")
        self.wait_for_continue()
