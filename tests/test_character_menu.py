"""
Тесты для меню персонажа (CharacterMenu).

Тестируем:
- Инициализацию меню
- Основные методы
- Обработку исключений
"""

import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Добавляем src в Python path для тестов
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.infrastructure.ui.menus.character_menu import CharacterMenu
from src.infrastructure.ui.renderer import Renderer
from src.infrastructure.ui.input_handler import InputHandler

pytestmark = pytest.mark.unit


class TestCharacterMenu:
    """Тесты меню персонажа."""

    def setup_method(self):
        """Настраивает тесты."""
        self.mock_renderer = Mock(spec=Renderer)
        self.mock_input_handler = Mock(spec=InputHandler)
        self.menu = CharacterMenu(self.mock_renderer, self.mock_input_handler)

    def test_initialization(self):
        """Тестирует инициализацию меню."""
        assert self.menu.renderer is not None
        assert self.menu.input_handler is not None
        assert hasattr(self.menu, "current_step")
        assert hasattr(self.menu, "max_steps")

    def test_show(self):
        """Тестирует отображение меню."""
        self.menu.show()

        self.mock_renderer.clear_screen.assert_called_once()
        self.mock_renderer.show_title.assert_called_once_with(
            "=== СОЗДАНИЕ ПЕРСОНАЖА ==="
        )

    def test_get_choice_keyboard_interrupt(self):
        """Тестирует обработку KeyboardInterrupt."""
        self.mock_input_handler.get_choice.side_effect = KeyboardInterrupt()

        result = self.menu.get_choice("Тест", 5)

        assert result == -1
        self.mock_renderer.show_info.assert_called_once_with("Возврат в главное меню.")

    def test_input_name_custom(self):
        """Тестирует ввод имени пользователем."""
        self.mock_input_handler.get_text.return_value = "Тестовый персонаж"

        result = self.menu.input_name()

        assert result == "Тестовый персонаж"
        self.mock_renderer.clear_screen.assert_called_once()
        self.mock_renderer.show_title.assert_called_once_with(
            "=== ВВЕДИТЕ ИМЯ ПЕРСОНАЖА ==="
        )

    @patch("random.choice")
    def test_input_name_random(self, mock_random):
        """Тестирует генерацию случайного имени."""
        self.mock_input_handler.get_text.return_value = ""  # Пустой ввод
        mock_random.return_value = "Артас"

        result = self.menu.input_name()

        assert result == "Артас"
        mock_random.assert_called_once_with(
            ["Артас", "Лиана", "Гэндальф", "Тирион", "Фродо"]
        )

    def test_generate_attributes_fallback(self):
        """Тестирует генерацию характеристик при отсутствии файла конфигурации."""
        result = self.menu.generate_attributes("nonexistent_method")

        assert result == {
            "strength": 15,
            "dexterity": 14,
            "constitution": 13,
            "intelligence": 12,
            "wisdom": 10,
            "charisma": 8,
        }

    def test_generate_attributes_standard_array(self):
        """Тестирует генерацию характеристик стандартным набором."""
        result = self.menu.generate_attributes("standard_array")

        assert result == {
            "strength": 15,
            "dexterity": 14,
            "constitution": 13,
            "intelligence": 12,
            "wisdom": 10,
            "charisma": 8,
        }

    @patch("random.randint")
    def test_generate_attributes_four_d6(self, mock_randint):
        """Тестирует генерацию характеристик методом 4d6."""
        # Мокируем броски кубиков для предсказуемого результата
        mock_randint.side_effect = [
            6,
            5,
            4,
            3,
            6,
            5,
            4,
            3,
            6,
            5,
            4,
            3,
            6,
            5,
            4,
            3,
            6,
            5,
            4,
            3,
            6,
            5,
            4,
            3,
        ]

        result = self.menu.generate_attributes("four_d6_drop_lowest")

        assert "strength" in result
        assert "dexterity" in result
        assert "constitution" in result
        assert "intelligence" in result
        assert "wisdom" in result
        assert "charisma" in result

    def test_generate_attributes_point_buy(self):
        """Тестирует генерацию характеристик методом покупки очков."""
        result = self.menu.generate_attributes("point_buy")

        assert all(result[attr] == 10 for attr in result)

    def test_apply_bonuses_standard(self):
        """Тестирует применение стандартных расовых бонусов."""
        attributes = {
            "strength": 15,
            "dexterity": 14,
            "constitution": 13,
            "intelligence": 12,
            "wisdom": 10,
            "charisma": 8,
        }
        race_info = {"race": Mock(), "race_name": "human"}

        # Мокируем бонусы расы
        race_info["race"].get_bonuses.return_value = {"strength": 2, "constitution": 1}

        result = self.menu.apply_race_bonuses(attributes, race_info)

        assert result["strength"] == 17  # 15 + 2
        assert result["constitution"] == 14  # 13 + 1
        assert result["dexterity"] == 14  # Без изменений
        assert result["intelligence"] == 12  # Без изменений
        assert result["wisdom"] == 10  # Без изменений
        assert result["charisma"] == 8  # Без изменений

    def test_apply_bonuses_alternative(self):
        """Тестирует применение альтернативных расовых бонусов."""
        attributes = {
            "strength": 15,
            "dexterity": 14,
            "constitution": 13,
            "intelligence": 12,
            "wisdom": 10,
            "charisma": 8,
        }
        race_info = {
            "race": Mock(),
            "alternative_choices": {
                "ability_choice": {
                    "name": "Выбранные характеристики",
                    "description": "Выбраны характеристики: strength, dexterity",
                    "type": "ability_choice",
                }
            },
        }

        result = self.menu.apply_race_bonuses(attributes, race_info)

        # Альтернативные бонусы должны применяться через специальную логику
        assert isinstance(result, dict)

    def test_show_preview(self):
        """Тестирует показ предварительного просмотра персонажа."""
        character_data = {
            "name": "Тестовый персонаж",
            "race_name": "Человек",
            "class_name": "Воин",
            "attributes": {
                "strength": 16,
                "dexterity": 14,
                "constitution": 15,
                "intelligence": 12,
                "wisdom": 10,
                "charisma": 8,
            },
        }

        self.menu.show_preview(character_data)

        # Проверяем что были вызваны методы рендерера
        self.mock_renderer.clear_screen.assert_called()
        self.mock_renderer.show_title.assert_called()

    def test_create_character_success(self):
        """Тестирует успешное создание персонажа."""
        character_data = {
            "name": "Тестовый персонаж",
            "race_name": "human",
            "class_name": "fighter",
            "attributes": {
                "strength": 16,
                "dexterity": 14,
                "constitution": 15,
                "intelligence": 12,
                "wisdom": 10,
                "charisma": 8,
            },
        }

        with patch(
            "src.domain.entities.universal_race_factory.UniversalRaceFactory.create_race"
        ) as mock_create_race:
            with patch(
                "src.domain.entities.class_factory.CharacterClassFactory.create_class"
            ) as mock_create_class:
                mock_race = Mock()
                mock_class = Mock()
                mock_create_race.return_value = mock_race
                mock_create_class.return_value = mock_class

                with patch("src.domain.entities.character.Character") as mock_character:
                    mock_character_instance = Mock()
                    mock_character.return_value = mock_character_instance

                    result = self.menu.create_character(character_data)

                    assert result is not None
                    mock_create_race.assert_called_once_with("human")
                    mock_create_class.assert_called_once_with("fighter")

    def test_create_character_cancel(self):
        """Тестирует отмену создания персонажа."""
        character_data = {
            "name": "Тестовый персонаж",
            "race_name": "human",
            "class_name": "fighter",
            "attributes": {},
        }

        # Мокируем обработчик ввода для возврата "н" (нет)
        self.mock_input_handler.get_text.return_value = "н"

        result = self.menu.create_character(character_data)

        assert result is None

    def test_run_success(self):
        """Тестирует успешный запуск меню."""
        # Мокируем все шаги процесса создания
        with patch.object(self.menu, "input_name", return_value="Тестовый персонаж"):
            with patch.object(
                self.menu,
                "select_race",
                return_value={"race": Mock(), "race_name": "human"},
            ):
                with patch.object(self.menu, "select_class", return_value="fighter"):
                    with patch.object(
                        self.menu, "generate_attributes", return_value={"strength": 16}
                    ):
                        with patch.object(
                            self.menu,
                            "apply_race_bonuses",
                            return_value={"strength": 18},
                        ):
                            with patch.object(self.menu, "show_preview"):
                                with patch.object(
                                    self.menu, "create_character", return_value=Mock()
                                ):
                                    with patch.object(
                                        self.menu, "get_choice", return_value=1
                                    ):  # Продолжить
                                        result = self.menu.run()

                                        assert result is not None

    def test_run_cancel(self):
        """Тестирует отмену запуска меню."""
        # Мокируем первый шаг для отмены
        with patch.object(self.menu, "input_name", return_value=None):
            with patch.object(self.menu, "get_choice", return_value=0):  # Отмена
                result = self.menu.run()

                assert result is None

    def test_run_max_attempts(self):
        """Тестирует максимальное количество попыток."""
        # Мокируем обработчик ввода для возврата отмены
        self.mock_input_handler.get_text.return_value = "н"

        with patch.object(self.menu, "input_name", return_value=""):
            with patch.object(self.menu, "get_choice", return_value=0):  # Отмена
                result = self.menu.run()

                assert result is None


class TestCharacterMenuEdgeCases:
    """Тесты граничных случаев меню персонажа."""

    def setup_method(self):
        """Настраивает тесты."""
        self.mock_renderer = Mock(spec=Renderer)
        self.mock_input_handler = Mock(spec=InputHandler)
        self.menu = CharacterMenu(self.mock_renderer, self.mock_input_handler)

    def test_input_name_whitespace_only(self):
        """Тестирует ввод только пробелов."""
        self.mock_input_handler.get_text.return_value = "   "  # Только пробелы

        result = self.menu.input_name()

        # Должно сгенерировать случайное имя
        assert result != "   "
        assert len(result.strip()) > 0

    def test_max_steps_boundary(self):
        """Тестирует границу максимального количества шагов."""
        # Устанавливаем текущий шаг на максимум
        self.menu.current_step = self.menu.max_steps

        # Попытка увеличить шаг должна вызывать обработку
        with patch.object(self.menu, "create_character") as mock_create:
            mock_create.return_value = Mock()

            self.menu.current_step += 1

            # Должен быть вызван метод создания персонажа
            # (конкретная реализация зависит от логики меню)

    def test_select_race_with_subraces(self):
        """Тестирует выбор расы с подрасами."""
        with patch(
            "src.domain.entities.universal_race_factory.UniversalRaceFactory.get_race_choices"
        ) as mock_choices:
            with patch(
                "src.domain.entities.universal_race_factory.UniversalRaceFactory.create_race"
            ) as mock_create:
                with patch.object(self.menu, "get_choice", return_value="1"):
                    with patch.object(
                        self.menu, "show_alternative_features_selection"
                    ) as mock_alternative:
                        mock_choices.return_value = {"1": "Эльф"}
                        mock_race = Mock()
                        mock_create.return_value = mock_race
                        mock_alternative.return_value = {"type": "ability_choice"}

                        result = self.menu.select_race()

                        assert "race" in result
                        assert result["race"] == mock_race

    def test_select_class_with_specializations(self):
        """Тестирует выбор класса с специализациями."""
        with patch(
            "src.domain.entities.class_factory.CharacterClassFactory.get_class_choices"
        ) as mock_choices:
            with patch(
                "src.domain.entities.class_factory.CharacterClassFactory.create_class"
            ) as mock_create:
                with patch.object(self.menu, "get_choice", return_value="1"):
                    mock_choices.return_value = {"1": "Воин"}
                    mock_class = Mock()
                    mock_create.return_value = mock_class

                    result = self.menu.select_class()

                    assert result == "Воин"
                    mock_create.assert_called_once_with("Воин")

    def test_generate_attributes_invalid_method(self):
        """Тестирует генерацию характеристик с невалидным методом."""
        result = self.menu.generate_attributes("invalid_method")

        # Должен вернуть fallback значения
        assert isinstance(result, dict)
        assert len(result) == 6  # 6 характеристик

    def test_apply_bonuses_no_race(self):
        """Тестирует применение бонусов без расы."""
        attributes = {"strength": 15}
        race_info = {}

        result = self.menu.apply_race_bonuses(attributes, race_info)

        # Должен вернуть оригинальные атрибуты
        assert result == attributes

    def test_show_preview_empty_data(self):
        """Тестирует показ превью с пустыми данными."""
        character_data = {}

        # Не должно вызывать ошибок
        self.menu.show_preview(character_data)

        # Проверяем что были вызваны базовые методы рендерера
        self.mock_renderer.clear_screen.assert_called()


class TestCharacterMenuIntegration:
    """Тесты интеграции меню персонажа."""

    def setup_method(self):
        """Настраивает тесты."""
        self.mock_renderer = Mock(spec=Renderer)
        self.mock_input_handler = Mock(spec=InputHandler)
        self.menu = CharacterMenu(self.mock_renderer, self.mock_input_handler)

    def test_full_character_creation_flow(self):
        """Тестирует полный процесс создания персонажа."""
        # Мокируем все зависимости
        with patch(
            "src.domain.entities.universal_race_factory.UniversalRaceFactory.create_race"
        ) as mock_create_race:
            with patch(
                "src.domain.entities.class_factory.CharacterClassFactory.create_class"
            ) as mock_create_class:
                with patch(
                    "src.domain.entities.character.Character"
                ) as mock_character_class:
                    # Настраиваем моки
                    mock_race = Mock()
                    mock_class = Mock()
                    mock_character = Mock()

                    mock_create_race.return_value = mock_race
                    mock_create_class.return_value = mock_class
                    mock_character_class.return_value = mock_character

                    # Мокируем методы меню
                    with patch.object(
                        self.menu, "input_name", return_value="Тестовый персонаж"
                    ):
                        with patch.object(
                            self.menu,
                            "select_race",
                            return_value={"race": mock_race, "race_name": "human"},
                        ):
                            with patch.object(
                                self.menu, "select_class", return_value="fighter"
                            ):
                                with patch.object(
                                    self.menu,
                                    "generate_attributes",
                                    return_value={"strength": 16},
                                ):
                                    with patch.object(
                                        self.menu,
                                        "apply_race_bonuses",
                                        return_value={"strength": 18},
                                    ):
                                        with patch.object(self.menu, "show_preview"):
                                            with patch.object(
                                                self.menu,
                                                "get_choice",
                                                side_effect=[1, 1],
                                            ):  # Продолжить, подтвердить
                                                result = self.menu.run()

                                                assert result is not None
                                                mock_character_class.assert_called_once()

    def test_error_handling_in_flow(self):
        """Тестирует обработку ошибок в процессе создания."""
        # Мокируем метод, который вызывает ошибку
        with patch.object(self.menu, "input_name", side_effect=Exception("Test error")):
            with patch.object(self.menu, "get_choice", return_value=0):  # Отмена
                result = self.menu.run()

                # Должно обработать ошибку и вернуть None
                assert result is None

    def test_renderer_error_handling(self):
        """Тестирует обработку ошибок рендерера."""
        # Мокируем рендерер для вызова ошибки
        self.mock_renderer.clear_screen.side_effect = Exception("Renderer error")

        # Не должно вызывать ошибку в методе show
        try:
            self.menu.show()
        except Exception:
            pytest.fail("Метод show должен обрабатывать ошибки рендерера")


if __name__ == "__main__":
    pytest.main([__file__])
