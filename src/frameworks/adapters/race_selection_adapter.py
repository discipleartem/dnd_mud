"""Адаптер выбора расы.

Следует Clean Architecture - адаптер между UI и бизнес-логикой.
Реализует многоуровневое меню выбора расы и подрасы.
"""

from typing import Dict, List, Optional, Callable

from src.entities.menu_entity import MenuActionType, MenuItem, MenuState
from src.entities.race_entity import Race, Subrace, RaceSelectionResult
from src.interfaces.services.menu_service_interface import MenuServiceInterface
from src.interfaces.services.race_service_interface import RaceServiceInterface


class RaceSelectionAdapter:
    """Адаптер выбора расы.

    Следует Clean Architecture - предоставляет UI интерфейс
    для выбора расы и подрасы с интеграцией в существующую систему меню.
    """

    def __init__(
        self, 
        race_service: RaceServiceInterface,
        menu_service: MenuServiceInterface
    ) -> None:
        """Инициализация адаптера.

        Args:
            race_service: Сервис работы с расами
            menu_service: Сервис работы с меню
        """
        self._race_service = race_service
        self._menu_service = menu_service
        self._current_state: Optional[str] = "race_selection"

    def create_race_selection_menu(self) -> MenuState:
        """Создать главное меню выбора расы.

        Returns:
            Состояние меню со списком рас
        """
        races = self._race_service.load_races()
        menu_items = []

        for race in races:
            if race.subraces:
                # Раса с подрасами - переходим к выбору подрасы
                item = MenuItem(
                    id=f"race_{race.name}",
                    title=race.name,
                    description=f"{race.description} (нажмите для выбора подрасы)",
                    action_type=MenuActionType.NAVIGATION,
                    target_menu=f"subrace_{race.name}",
                    action=self._create_subrace_menu_action(race.name)
                )
            else:
                # Раса без подрас - можно выбрать сразу
                item = MenuItem(
                    id=f"race_{race.name}",
                    title=race.name,
                    description=race.description,
                    action_type=MenuActionType.ACTION,
                    action=self._create_select_race_action(race.name)
                )
            
            menu_items.append(item)

        return self._menu_service.create_menu_state(
            title="Выбор расы",
            items=menu_items
        )

    def _create_subrace_menu_action(self, race_name: str) -> Callable[[], MenuState]:
        """Создать действие для перехода к меню подрас.

        Args:
            race_name: Название расы

        Returns:
            Функция создающая меню подрас
        """
        def action() -> MenuState:
            return self._create_subrace_selection_menu(race_name)
        return action

    def _create_select_race_action(self, race_name: str) -> Callable[[], RaceSelectionResult]:
        """Создать действие для выбора расы.

        Args:
            race_name: Название расы

        Returns:
            Функция выбора расы
        """
        def action() -> RaceSelectionResult:
            return self._race_service.create_race_selection(race_name)
        return action

    def _create_subrace_selection_menu(self, race_name: str) -> MenuState:
        """Создать меню выбора подрасы.

        Args:
            race_name: Название родительской расы

        Returns:
            Состояние меню со списком подрас
        """
        race = self._race_service.get_race(race_name)
        if not race or not race.subraces:
            # Возврат к главному меню если что-то пошло не так
            return self.create_race_selection_menu()

        menu_items = []
        
        # Добавляем пункт возврата
        back_item = MenuItem(
            id="0",
            title="Назад",
            description="Вернуться к выбору расы",
            action_type=MenuActionType.BACK,
            action=self.create_race_selection_menu
        )
        menu_items.append(back_item)

        # Добавляем подрасы
        for subrace in race.subraces:
            item = MenuItem(
                id=f"subrace_{subrace.name}",
                title=subrace.name,
                description=f"{subrace.description}\n"
                          f"Бонусы: {subrace.ability_bonuses_description}",
                action_type=MenuActionType.ACTION,
                action=self._create_select_subrace_action(race_name, subrace.name)
            )
            menu_items.append(item)

        return self._menu_service.create_menu_state(
            title=f"Выбор подрасы: {race.name}",
            items=menu_items
        )

    def _create_select_subrace_action(
        self, race_name: str, subrace_name: str
    ) -> Callable[[], RaceSelectionResult]:
        """Создать действие для выбора подрасы.

        Args:
            race_name: Название расы
            subrace_name: Название подрасы

        Returns:
            Функция выбора подрасы
        """
        def action() -> RaceSelectionResult:
            return self._race_service.create_race_selection(race_name, subrace_name)
        return action

    def get_race_details(self, race_name: str, subrace_name: Optional[str] = None) -> str:
        """Получить детальное описание расы/подрасы.

        Args:
            race_name: Название расы
            subrace_name: Название подрасы (опционально)

        Returns:
            Форматированное описание
        """
        race = self._race_service.get_race(race_name)
        if not race:
            return "Раса не найдена"

        details = [f"=== {race.name} ==="]
        details.append(f"Описание: {race.description}")
        details.append(f"Скорость: {race.speed}")
        details.append(f"Размер: {race.size}")
        details.append(f"Языки: {', '.join(race.languages)}")
        
        if race.ability_bonuses:
            bonuses_str = ', '.join([f"{k}: +{v}" for k, v in race.ability_bonuses.items()])
            details.append(f"Бонусы к характеристикам: {bonuses_str}")

        if subrace_name:
            subrace = self._race_service.get_subrace(race_name, subrace_name)
            if subrace:
                details.append(f"\n--- {subrace.name} ---")
                details.append(f"Описание: {subrace.description}")
                
                if subrace.ability_bonuses:
                    bonuses_str = ', '.join([f"{k}: +{v}" for k, v in subrace.ability_bonuses.items()])
                    details.append(f"Дополнительные бонусы: {bonuses_str}")

                if subrace.features:
                    details.append("Особенности:")
                    for feature in subrace.features:
                        details.append(f"  • {feature.get('name', 'Без названия')}: "
                                      f"{feature.get('description', 'Нет описания')}")

        return '\n'.join(details)

    def validate_race_choice(self, race_name: str, subrace_name: Optional[str] = None) -> bool:
        """Валидировать выбор расы и подрасы.

        Args:
            race_name: Название расы
            subrace_name: Название подрасы (опционально)

        Returns:
            True если выбор валиден, иначе False
        """
        return self._race_service.validate_race_choice(race_name, subrace_name)

    def get_available_races(self) -> List[str]:
        """Получить список доступных рас.

        Returns:
            Список названий рас
        """
        races = self._race_service.load_races()
        return [race.name for race in races]

    def get_subraces_for_race(self, race_name: str) -> List[str]:
        """Получить список подрас для указанной расы.

        Args:
            race_name: Название расы

        Returns:
            Список названий подрас
        """
        race = self._race_service.get_race(race_name)
        if not race or not race.subraces:
            return []
        
        return [subrace.name for subrace in race.subraces]
