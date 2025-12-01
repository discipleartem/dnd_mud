"""
Character Creator - создание персонажа
"""
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from typing import Dict, Any, Optional
import logging
import json
from pathlib import Path
from datetime import datetime


class CharacterCreator:
    """Создание нового персонажа"""

    def __init__(self, config_manager, window_manager, data_loader):
        self.config_manager = config_manager
        self.window_manager = window_manager
        self.data_loader = data_loader
        self.console = Console()
        self.logger = logging.getLogger(__name__)

        self.character: Dict[str, Any] = {}
        self.saves_path = Path(config_manager.get('paths.saves', 'game/saves'))

    def create_character(self) -> Optional[Dict[str, Any]]:
        """
        Процесс создания персонажа

        Returns:
            Словарь с данными персонажа или None если отменено
        """
        self.logger.info("Начало создания персонажа")

        # Инициализация персонажа
        self.character = {
            'name': '',
            'race': '',
            'class': '',
            'level': 1,
            'experience': 0,
            'abilities': {},
            'hp_max': 0,
            'hp_current': 0,
            'created_at': datetime.now().isoformat(),
            'playtime_seconds': 0
        }

        # Шаги создания персонажа
        steps = [
            ('name', self._choose_name, "Имя персонажа"),
            ('race', self._choose_race, "Раса"),
            ('class', self._choose_class, "Класс"),
            ('abilities', self._set_abilities, "Характеристики"),
        ]

        for step_name, step_func, step_title in steps:
            self.window_manager.clear_screen()
            self._show_progress(step_title, steps.index((step_name, step_func, step_title)) + 1, len(steps))

            result = step_func()

            if result is None:  # Отмена
                if self._confirm_cancel():
                    return None
                continue

        # Финализация персонажа
        self._finalize_character()

        # Показываем итоговую информацию
        self._show_character_summary()

        # Сохраняем персонажа
        if self._save_character():
            self.logger.info(f"Персонаж создан: {self.character['name']}")
            return self.character

        return None

    def _show_progress(self, title: str, current: int, total: int):
        """Показать прогресс создания"""
        progress_text = f"Шаг {current} из {total}: {title}"
        panel = Panel(
            Text(progress_text, style="bold cyan"),
            border_style="cyan"
        )
        self.console.print(panel)
        self.console.print()

    def _choose_name(self) -> str:
        """Выбор имени персонажа"""
        self.console.print("[bold yellow]Введите имя вашего персонажа:[/bold yellow]")

        while True:
            name = input("\nИмя: ").strip()

            if not name:
                self.console.print("[red]Имя не может быть пустым![/red]")
                continue

            if len(name) < 2 or len(name) > 30:
                self.console.print("[red]Имя должно быть от 2 до 30 символов![/red]")
                continue

            # Проверка на существование
            if self._character_exists(name):
                self.console.print("[red]Персонаж с таким именем уже существует![/red]")
                overwrite = input("Перезаписать? (y/n): ").lower()
                if overwrite != 'y':
                    continue

            self.character['name'] = name
            return name

    def _choose_race(self) -> Optional[str]:
        """Выбор расы"""
        races = self.data_loader.load_races()

        if not races or 'races' not in races:
            self.console.print("[red]Ошибка загрузки рас![/red]")
            input("Нажмите Enter...")
            return None

        races_data = races['races']

        self.console.print("[bold yellow]Выберите расу:[/bold yellow]\n")

        # Таблица рас
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("№", style="dim", width=4)
        table.add_column("Раса", style="bold")
        table.add_column("Описание")

        race_keys = list(races_data.keys())
        for idx, race_key in enumerate(race_keys, 1):
            race_info = races_data[race_key]
            table.add_row(
                str(idx),
                race_info.get('name', race_key),
                race_info.get('description', '')[:50] + "..."
            )

        self.console.print(table)

        # Выбор
        while True:
            choice = input(f"\nВыберите расу (1-{len(race_keys)}): ").strip()

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(race_keys):
                    selected_race = race_keys[idx]
                    self.character['race'] = selected_race
                    self.character['race_data'] = races_data[selected_race]
                    return selected_race
            except ValueError:
                pass

            self.console.print("[red]Неверный выбор![/red]")

    def _choose_class(self) -> Optional[str]:
        """Выбор класса"""
        classes = self.data_loader.load_classes()

        if not classes or 'classes' not in classes:
            self.console.print("[red]Ошибка загрузки классов![/red]")
            input("Нажмите Enter...")
            return None

        classes_data = classes['classes']

        self.console.print("[bold yellow]Выберите класс:[/bold yellow]\n")

        # Таблица классов
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("№", style="dim", width=4)
        table.add_column("Класс", style="bold")
        table.add_column("Описание")
        table.add_column("Кость хитов", justify="center")

        class_keys = list(classes_data.keys())
        for idx, class_key in enumerate(class_keys, 1):
            class_info = classes_data[class_key]
            table.add_row(
                str(idx),
                class_info.get('name', class_key),
                class_info.get('description', '')[:40] + "...",
                f"d{class_info.get('hit_die', 6)}"
            )

        self.console.print(table)

        # Выбор
        while True:
            choice = input(f"\nВыберите класс (1-{len(class_keys)}): ").strip()

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(class_keys):
                    selected_class = class_keys[idx]
                    self.character['class'] = selected_class
                    self.character['class_data'] = classes_data[selected_class]
                    return selected_class
            except ValueError:
                pass

            self.console.print("[red]Неверный выбор![/red]")

    def _set_abilities(self) -> Dict[str, int]:
        """Установка характеристик"""
        self.console.print("[bold yellow]Распределение характеристик:[/bold yellow]\n")
        self.console.print("Стандартный набор: 15, 14, 13, 12, 10, 8\n")

        abilities = ['Сила', 'Ловкость', 'Телосложение', 'Интеллект', 'Мудрость', 'Харизма']
        ability_keys = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']
        standard_array = [15, 14, 13, 12, 10, 8]

        assigned = {}
        remaining = standard_array.copy()

        for ability, key in zip(abilities, ability_keys):
            self.console.print(f"\n[cyan]{ability}[/cyan]")
            self.console.print(f"Доступные значения: {remaining}")

            while True:
                try:
                    value = int(input(f"Значение для {ability}: ").strip())
                    if value in remaining:
                        assigned[key] = value
                        remaining.remove(value)
                        break
                    else:
                        self.console.print("[red]Это значение недоступно![/red]")
                except ValueError:
                    self.console.print("[red]Введите число![/red]")

        self.character['abilities'] = assigned
        return assigned

    def _finalize_character(self):
        """Финализация персонажа"""
        # Вычисляем HP
        class_data = self.character.get('class_data', {})
        hit_die = class_data.get('hit_die', 6)
        con_modifier = (self.character['abilities'].get('constitution', 10) - 10) // 2

        self.character['hp_max'] = hit_die + con_modifier
        self.character['hp_current'] = self.character['hp_max']

    def _show_character_summary(self):
        """Показать итоговую информацию о персонаже"""
        self.window_manager.clear_screen()

        self.console.print(Panel(
            Text("ПЕРСОНАЖ СОЗДАН!", style="bold green"),
            border_style="green"
        ))
        self.console.print()

        # Информация о персонаже
        info = f"""
[bold cyan]Имя:[/bold cyan] {self.character['name']}
[bold cyan]Раса:[/bold cyan] {self.character['race_data']['name']}
[bold cyan]Класс:[/bold cyan] {self.character['class_data']['name']}
[bold cyan]Уровень:[/bold cyan] {self.character['level']}
[bold cyan]HP:[/bold cyan] {self.character['hp_current']}/{self.character['hp_max']}

[bold yellow]Характеристики:[/bold yellow]
  Сила: {self.character['abilities']['strength']}
  Ловкость: {self.character['abilities']['dexterity']}
  Телосложение: {self.character['abilities']['constitution']}
  Интеллект: {self.character['abilities']['intelligence']}
  Мудрость: {self.character['abilities']['wisdom']}
  Харизма: {self.character['abilities']['charisma']}
        """

        self.console.print(info)
        input("\nНажмите Enter для продолжения...")

    def _save_character(self) -> bool:
        """Сохранение персонажа"""
        try:
            self.saves_path.mkdir(parents=True, exist_ok=True)

            filename = f"{self.character['name']}.json"
            filepath = self.saves_path / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.character, f, ensure_ascii=False, indent=2)

            self.console.print(f"\n[green]Персонаж сохранен: {filepath}[/green]")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка сохранения персонажа: {e}")
            self.console.print(f"\n[red]Ошибка сохранения: {e}[/red]")
            return False

    def _character_exists(self, name: str) -> bool:
        """Проверка существования персонажа"""
        filepath = self.saves_path / f"{name}.json"
        return filepath.exists()

    def _confirm_cancel(self) -> bool:
        """Подтверждение отмены создания"""
        choice = input("\nОтменить создание персонажа? (y/n): ").lower()
        return choice == 'y'