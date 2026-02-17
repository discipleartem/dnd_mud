"""
Меню настроек D&D MUD.

Применяемые паттерны:
- Menu (Меню) — пошаговый интерфейс настроек
- Controller (Контроллер) — обработка пользовательского ввода
- Observer (Наблюдатель) — обновление интерфейса при изменениях

Применяемые принципы:
- Single Responsibility — каждый класс отвечает за свою группу настроек
- Open/Closed — легко добавить новые категории настроек
- Dependency Inversion — зависимость от абстракций бизнес-логики
"""

from typing import Optional
from enum import Enum

from ....domain.services.game_config import game_config, ModInfo, AdventureInfo
from ....domain.services.level_resolver import level_resolver
from ..input_handler import InputHandler
from ..renderer import Renderer


class SettingsCategory(Enum):
    """Категории настроек."""

    MODS = "mods"
    ADVENTURES = "adventures"
    GAMEPLAY = "gameplay"
    BACK = "back"


class SettingsMenu:
    """Меню настроек игры."""

    def __init__(self, input_handler: InputHandler, renderer: Renderer):
        """Инициализирует меню настроек."""
        self.input_handler = input_handler
        self.renderer = renderer
        self.current_category = SettingsCategory.MODS

    def run(self) -> None:
        """Запускает меню настроек."""
        max_attempts = 20
        attempts = 0

        while attempts < max_attempts and self.current_category != SettingsCategory.BACK:
            attempts += 1
            try:
                self._handle_current_category()
            except KeyboardInterrupt:
                self._handle_cancellation()
                return
            except Exception as e:
                self.renderer.render_error(f"Ошибка: {e}")
                self.input_handler.wait_for_enter()

    def _handle_current_category(self) -> None:
        """Обрабатывает текущую категорию настроек."""
        self.renderer.clear_screen()
        self.renderer.render_title("Настройки игры")

        # Показываем основные категории
        print("\nВыберите категорию настроек:")
        print("1. Модификации")
        print("2. Приключения")
        print("3. Геймплей")
        print("4. Вернуться в главное меню")

        choice = self.input_handler.get_int(
            "\nВаш выбор: ", min_value=1, max_value=4
        )

        if choice == 1:
            self._handle_mods_settings()
        elif choice == 2:
            self._handle_adventures_settings()
        elif choice == 3:
            self._handle_gameplay_settings()
        else:
            self.current_category = SettingsCategory.BACK

    def _handle_mods_settings(self) -> None:
        """Обрабатывает настройки модов."""
        max_attempts = 50
        attempts = 0

        while attempts < max_attempts:
            attempts += 1
            self.renderer.clear_screen()
            self.renderer.render_title("Настройки модификаций")

            mods = game_config.get_available_mods()
            
            if not mods:
                print("\nМодификации не найдены.")
                self.input_handler.wait_for_enter()
                return

            print("\nДоступные модификации:")
            for i, mod in enumerate(mods, 1):
                status = "✓ Активна" if mod.is_active else "○ Неактивна"
                level_info = f" (уровень {mod.starting_level})" if mod.starting_level else ""
                print(f"{i}. {mod.name} {status}{level_info}")
                print(f"   {mod.description}")

            print(f"\n{len(mods) + 1}. Вернуться назад")

            choice = self.input_handler.get_int(
                "\nВыберите мод для toggling или вернитесь назад: ",
                min_value=1,
                max_value=len(mods) + 1
            )

            if choice == len(mods) + 1:
                return

            selected_mod = mods[choice - 1]
            self._toggle_mod(selected_mod)

    def _toggle_mod(self, mod: ModInfo) -> None:
        """Переключает активацию мода."""
        if mod.is_active:
            # Деактивируем
            success = game_config.deactivate_mod(mod.folder_name)
            if success:
                self.renderer.render_success(f"Мод '{mod.name}' деактивирован")
            else:
                self.renderer.render_error(f"Не удалось деактивировать мод '{mod.name}'")
        else:
            # Активируем
            success = game_config.activate_mod(mod.folder_name)
            if success:
                self.renderer.render_success(f"Мод '{mod.name}' активирован")
            else:
                self.renderer.render_error(f"Не удалось активировать мод '{mod.name}'")

        self.input_handler.wait_for_enter()

    def _handle_adventures_settings(self) -> None:
        """Обрабатывает настройки приключений."""
        max_attempts = 50
        attempts = 0

        while attempts < max_attempts:
            attempts += 1
            self.renderer.clear_screen()
            self.renderer.render_title("Настройки приключений")

            adventures = game_config.get_available_adventures()
            
            if not adventures:
                print("\nПриключения не найдены.")
                self.input_handler.wait_for_enter()
                return

            print("\nДоступные приключения:")
            for i, adventure in enumerate(adventures, 1):
                status = "✓ Активно" if adventure.is_active else "○ Неактивно"
                level_info = f" (уровень {adventure.recommended_level})" if adventure.recommended_level else ""
                print(f"{i}. {adventure.name} {status}{level_info}")
                print(f"   {adventure.description}")
                print(f"   Сложность: {adventure.difficulty}")

            # Показываем текущие настройки отображения
            show_all = game_config.get_show_all_adventures()
            print(f"\nНастройки отображения:")
            print(f"• Показывать все приключения: {'Да' if show_all else 'Нет'}")

            print(f"\n{len(adventures) + 1}. Выбрать приключение")
            print(f"{len(adventures) + 2}. Переключить отображение всех приключений")
            print(f"{len(adventures) + 3}. Вернуться назад")

            choice = self.input_handler.get_int(
                "\nВаш выбор: ",
                min_value=1,
                max_value=len(adventures) + 3
            )

            if choice == len(adventures) + 1:
                self._select_adventure(adventures)
            elif choice == len(adventures) + 2:
                self._toggle_show_all_adventures()
            elif choice == len(adventures) + 3:
                return
            else:
                selected_adventure = adventures[choice - 1]
                self._toggle_adventure(selected_adventure)

    def _select_adventure(self, adventures: list[AdventureInfo]) -> None:
        """Выбирает активное приключение."""
        print("\nВыберите активное приключение:")
        for i, adventure in enumerate(adventures, 1):
            print(f"{i}. {adventure.name}")

        choice = self.input_handler.get_int(
            "\nВаш выбор: ", min_value=1, max_value=len(adventures)
        )

        selected_adventure = adventures[choice - 1]
        success = game_config.set_active_adventure(selected_adventure.file_name)
        
        if success:
            self.renderer.render_success(f"Приключение '{selected_adventure.name}' выбрано")
        else:
            self.renderer.render_error(f"Не удалось выбрать приключение '{selected_adventure.name}'")

        self.input_handler.wait_for_enter()

    def _toggle_adventure(self, adventure: AdventureInfo) -> None:
        """Переключает активацию приключения."""
        if adventure.is_active:
            # Деактивируем (устанавливаем None)
            success = game_config.set_active_adventure("")
            if success:
                self.renderer.render_success(f"Приключение '{adventure.name}' деактивировано")
            else:
                self.renderer.render_error(f"Не удалось деактивировать приключение '{adventure.name}'")
        else:
            # Активируем
            success = game_config.set_active_adventure(adventure.file_name)
            if success:
                self.renderer.render_success(f"Приключение '{adventure.name}' активировано")
            else:
                self.renderer.render_error(f"Не удалось активировать приключение '{adventure.name}'")

        self.input_handler.wait_for_enter()

    def _toggle_show_all_adventures(self) -> None:
        """Переключает отображение всех приключений."""
        current = game_config.get_show_all_adventures()
        game_config.set_show_all_adventures(not current)
        
        status = "включено" if not current else "выключено"
        self.renderer.render_success(f"Отображение всех приключений {status}")
        self.input_handler.wait_for_enter()

    def _handle_gameplay_settings(self) -> None:
        """Обрабатывает настройки геймплея."""
        max_attempts = 50
        attempts = 0

        while attempts < max_attempts:
            attempts += 1
            self.renderer.clear_screen()
            self.renderer.render_title("Настройки геймплея")

            # Показываем текущий уровень
            current_level = game_config.get_default_starting_level()
            level_info = level_resolver.get_level_info()
            
            print(f"\nТекущие настройки:")
            print(f"• Начальный уровень по умолчанию: {current_level}")
            print(f"• Текущий начальный уровень: {level_info['final_level']}")
            print(f"• Источник уровня: {level_info['active_source']}")

            print(f"\nДействия:")
            print("1. Изменить начальный уровень по умолчанию")
            print("2. Показать информацию об определении уровня")
            print("3. Вернуться назад")

            choice = self.input_handler.get_int(
                "\nВаш выбор: ", min_value=1, max_value=3
            )

            if choice == 1:
                self._change_default_level()
            elif choice == 2:
                self._show_level_info()
            else:
                return

    def _change_default_level(self) -> None:
        """Изменяет начальный уровень по умолчанию."""
        current = game_config.get_default_starting_level()
        
        new_level = self.input_handler.get_int(
            f"\nВведите новый начальный уровень (1-20): ",
            min_value=1,
            max_value=20,
            default=current
        )

        game_config.set_default_starting_level(new_level)
        self.renderer.render_success(f"Начальный уровень по умолчанию изменен на {new_level}")
        self.input_handler.wait_for_enter()

    def _show_level_info(self) -> None:
        """Показывает подробную информацию об определении уровня."""
        level_info = level_resolver.get_level_info()
        
        self.renderer.clear_screen()
        self.renderer.render_title("Информация об определении уровня")
        
        print(f"\nФинальный уровень: {level_info['final_level']}")
        print(f"Активный источник: {level_info['active_source']}")
        
        print(f"\nВсе источники (по приоритету):")
        for source in level_info['all_sources']:
            status = "✓" if source['is_active'] else "○"
            print(f"{status} {source['name']} (приоритет {source['priority']}) -> уровень {source['level']}")

        self.input_handler.wait_for_enter()

    def _handle_cancellation(self) -> None:
        """Обрабатывает отмену настроек."""
        self.renderer.render_info("Настройки отменены")


class SettingsController:
    """Контроллер настроек игры."""

    def __init__(self, input_handler: InputHandler, renderer: Renderer):
        """Инициализирует контроллер."""
        self.input_handler = input_handler
        self.renderer = renderer

    def show_settings(self) -> None:
        """Показывает меню настроек."""
        menu = SettingsMenu(self.input_handler, self.renderer)
        menu.run()


# Пример использования
if __name__ == "__main__":
    # Для тестирования потребуется мокинг InputHandler и Renderer
    print("Модуль настроек готов к использованию")
