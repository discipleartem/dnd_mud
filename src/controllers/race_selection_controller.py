"""Контроллер выбора расы.

Следует Clean Architecture - адаптер между UI и бизнес-логикой.
Координирует процесс выбора расы и подрасы.
"""

from typing import Optional

from src.dependency_injection import ApplicationServices
from src.entities.race_entity import RaceSelectionResult
from src.frameworks.adapters.race_selection_adapter import RaceSelectionAdapter


class RaceSelectionController:
    """Контроллер выбора расы.

    Следует Clean Architecture - управляет процессом выбора
    расы и подрасы, интегрируясь с существующей системой меню.
    """

    def __init__(self, services: Optional[ApplicationServices] = None) -> None:
        """Инициализация контроллера.

        Args:
            services: Сервисы приложения
        """
        self._services = services or ApplicationServices()
        self._adapter = RaceSelectionAdapter(
            race_service=self._services.race_service,
            menu_service=self._services.menu_service
        )

    def show_race_selection(self) -> RaceSelectionResult:
        """Показать меню выбора расы.

        Returns:
            Результат выбора расы
        """
        current_menu = self._adapter.create_race_selection_menu()
        
        while True:
            # Отображаем текущее меню
            self._display_menu(current_menu)
            
            # Получаем выбор пользователя
            choice = self._get_user_choice(current_menu)
            
            if choice is None:
                continue

            # Обрабатываем выбор
            if choice.action_type.value == "back":
                if current_menu.title == "Выбор расы":
                    # Выход из меню выбора расы
                    raise KeyboardInterrupt("Выбор расы отменён")
                else:
                    # Возврат к предыдущему меню
                    current_menu = choice.action()
            elif choice.action_type.value == "navigation":
                # Переход к подменю
                current_menu = choice.action()
            elif choice.action_type.value == "action":
                # Выполнение действия (выбор расы/подрасы)
                try:
                    result = choice.action()
                    self._display_selection_result(result)
                    return result
                except ValueError as e:
                    self._display_error(f"Ошибка: {e}")
                    continue
            elif choice.action_type.value == "exit":
                raise KeyboardInterrupt("Выход из программы")

    def _display_menu(self, menu_state) -> None:
        """Отобразить меню.

        Args:
            menu_state: Состояние меню для отображения
        """
        print(f"\n=== {menu_state.title} ===")
        
        for i, item in enumerate(menu_state.items, 1):
            if item.is_visible:
                hotkey = f" [{item.hotkey}]" if item.hotkey else ""
                status = "" if item.is_enabled else " (недоступно)"
                print(f"{i}. {item.title}{hotkey}{status}")
                if item.description:
                    print(f"   {item.description}")

    def _get_user_choice(self, menu_state):
        """Получить выбор пользователя.

        Args:
            menu_state: Текущее состояние меню

        Returns:
            Выбранный пункт меню или None
        """
        while True:
            try:
                choice_input = input("\nВаш выбор (или 'q' для выхода): ").strip()
                
                if choice_input.lower() == 'q':
                    from src.entities.menu_entity import MenuItem, MenuActionType
                    return MenuItem(
                        id="exit",
                        title="Выход",
                        action_type=MenuActionType.EXIT
                    )
                
                # Проверяем горячие клавиши
                for item in menu_state.items:
                    if item.hotkey and choice_input.lower() == item.hotkey.lower():
                        return item
                
                # Проверяем числовой выбор
                if choice_input.isdigit():
                    choice_index = int(choice_input) - 1
                    if 0 <= choice_index < len(menu_state.items):
                        item = menu_state.items[choice_index]
                        if item.is_enabled:
                            return item
                        else:
                            print("Этот пункт недоступен.")
                            continue
                
                print("Некорректный выбор. Попробуйте снова.")
                
            except KeyboardInterrupt:
                from src.entities.menu_entity import MenuItem, MenuActionType
                return MenuItem(
                    id="exit",
                    title="Выход",
                    action_type=MenuActionType.EXIT
                )
            except EOFError:
                from src.entities.menu_entity import MenuItem, MenuActionType
                return MenuItem(
                    id="exit",
                    title="Выход",
                    action_type=MenuActionType.EXIT
                )

    def _display_selection_result(self, result: RaceSelectionResult) -> None:
        """Отобразить результат выбора расы.

        Args:
            result: Результат выбора расы
        """
        print(f"\n🎉 Выбрана раса: {result.race_name}")
        
        if result.subrace_name:
            print(f"🎯 Подраса: {result.subrace_name}")
        
        print("\n📊 Применённые бонусы:")
        for ability, bonus in result.applied_bonuses.items():
            print(f"  {ability}: +{bonus}")
        
        print("\n📈 Итоговые характеристики:")
        for ability, value in result.final_abilities.items():
            print(f"  {ability}: {value}")

    def _display_error(self, message: str) -> None:
        """Отобразить ошибку.

        Args:
            message: Текст ошибки
        """
        print(f"\n❌ {message}")

    def get_adapter(self) -> RaceSelectionAdapter:
        """Получить адаптер выбора расы.

        Returns:
            Адаптер выбора расы
        """
        return self._adapter
