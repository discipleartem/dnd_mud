"""Главная точка входа в D&D Text MUD.

Следует Clean Architecture - точка входа с Dependency Injection.
Оркестрация всех компонентов через DI контейнер.
"""

import sys

from src.dependency_injection import ApplicationServices, get_container
from src.dto.welcome_dto import WelcomeControllerRequest
from src.dto.menu_dto import MenuControllerRequest
from src.dto.settings_dto import SettingsControllerRequest
from src.dto.save_game_dto import SaveGameRequest
from src.frameworks.console.welcome_adapter import ConsoleWelcomeScreenAdapter
from src.frameworks.console.load_game_adapter import LoadGameMenuAdapter
from src.controllers.race_selection_controller import RaceSelectionController


class Application:
    """Основной класс приложения.
    
    Следует Clean Architecture - оркестрация Use Cases через
    Dependency Injection контейнер.
    """

    def __init__(self) -> None:
        """Инициализация приложения."""
        self._services = ApplicationServices()
        self._welcome_controller = self._services.welcome_controller
        self._main_menu_controller = self._services.main_menu_controller
        self._settings_controller = self._services.settings_controller
        self._save_game_controller = self._services.save_game_controller
        self._race_selection_controller = RaceSelectionController(self._services)
        self._welcome_adapter = ConsoleWelcomeScreenAdapter(use_colors=True)
        self._load_game_adapter = LoadGameMenuAdapter(use_colors=True)
        
        # Включаем режим главного меню
        self._welcome_adapter.enable_main_menu()

    def run_welcome_screen(self) -> None:
        """Запустить приветственный экран с главным меню."""
        print("Запуск главного меню...")

        # Создаем главное меню вместо простого приветствия
        menu_response = self._main_menu_controller.create_main_menu(language="ru")
        
        if menu_response.success:
            # Отображаем главное меню
            self._welcome_adapter.display_main_menu(menu_response)
            
            # Главный цикл меню
            self._run_main_menu_loop(menu_response)
        else:
            print(f"Ошибка создания меню: {menu_response.message}")

        print("Главное меню завершено")

    def _run_main_menu_loop(self, initial_menu_response) -> None:
        """Запустить главный цикл меню.
        
        Args:
            initial_menu_response: Начальное состояние меню
        """
        current_menu_state = initial_menu_response.menu_state
        
        while True:
            try:
                # Получаем ввод пользователя
                user_input = self._welcome_adapter.get_user_input()
                
                if not user_input:
                    continue
                
                # Обрабатываем специальные команды
                if user_input.lower() in ["exit", "quit", "6"]:
                    print("Выход из игры...")
                    break
                
                # Создаем запрос на обработку выбора
                menu_request = MenuControllerRequest(
                    action="select",
                    selection=user_input
                )
                
                # Обрабатываем выбор
                response = self._main_menu_controller.handle_navigation(menu_request)
                
                if response.success:
                    # Проверяем результат действия
                    if response.action_result:
                        action = response.action_result.get("action", "")
                        navigation = response.action_result.get("navigation", "")
                        
                        if action == "exit":
                            print("Выход из игры...")
                            break
                        elif action == "new_game":
                            print("Запуск новой игры...")
                            self._handle_new_game()
                        elif action == "create_character":
                            print("Создание персонажа...")
                            self._handle_create_character()
                        elif action == "load_game":
                            print("Загрузка игры...")
                            self._handle_load_game()
                        elif navigation == "settings":
                            print("Открытие настроек...")
                            self._handle_settings()
                        elif navigation == "languages":
                            print("Открытие языков...")
                            self._handle_languages()
                    
                    # Обновляем состояние меню если изменилось
                    if response.menu_state:
                        current_menu_state = response.menu_state
                        self._welcome_adapter.refresh_display()
                else:
                    # Показываем ошибку и обновляем отображение
                    self._welcome_adapter.display_message(
                        response.message, 
                        "error"
                    )
                    self._welcome_adapter.refresh_display()
                    
            except KeyboardInterrupt:
                print("\nПрерывание пользователем")
                break
            except Exception as e:
                print(f"Ошибка в главном цикле: {e}")
                break

    def _handle_new_game(self) -> None:
        """Обработать выбор 'Новая игра'."""
        try:
            # Создаем тестовое сохранение для демонстрации
            character_data = {
                "name": "Тестовый персонаж",
                "level": 1,
                "class": "Воин",
                "race": "Человек",
                "background": "Воин",
                "abilities": {
                    "strength": 16,
                    "dexterity": 14,
                    "constitution": 15,
                    "intelligence": 12,
                    "wisdom": 13,
                    "charisma": 10
                },
                "hp": 12,
                "ac": 16,
                "equipment": ["длинный меч", "кожаный доспех", "щит"],
                "gold": 10
            }
            
            # Используем быстрое сохранение
            response = self._save_game_controller.quick_save(
                character_name=character_data["name"],
                character_level=character_data["level"],
                character_class=character_data["class"],
                character_data=character_data,
                location="Таверна 'Серый Волк'"
            )
            
            if response.success:
                save_info = response.save_game
                self._welcome_adapter.display_message(
                    f"✅ Новая игра создана и сохранена в слот {save_info['slot_number']}", 
                    "success"
                )
                self._welcome_adapter.display_message(
                    f"Персонаж: {save_info['character_name']} (уровень {save_info['character_level']} {save_info['character_class']})", 
                    "info"
                )
            else:
                self._welcome_adapter.display_message(
                    f"❌ Ошибка создания новой игры: {response.message}", 
                    "error"
                )
                
        except Exception as e:
            self._welcome_adapter.display_message(
                f"Ошибка при создании новой игры: {str(e)}", 
                "error"
            )
        
        input("Нажмите Enter для продолжения...")

    def _handle_create_character(self) -> None:
        """Обработать выбор 'Создать персонажа'."""
        try:
            # Используем наш новый RaceSelectionController
            result = self._race_selection_controller.show_race_selection()
            
            if result:
                # Сохраняем результат выбора расы
                print(f"\n🎉 Раса выбрана: {result.race_name}")
                if result.subrace_name:
                    print(f"🎯 Подраса: {result.subrace_name}")
                
                print(f"\n📊 Итоговые характеристики:")
                for ability, value in result.final_abilities.items():
                    print(f"  {ability.capitalize()}: {value}")
                
                # Здесь будет интеграция со следующим этапом (генерация характеристик)
                print("\n✅ Выбор расы завершён. Переходим к следующему этапу...")
                input("Нажмите Enter для продолжения...")
            else:
                print("\n❌ Выбор расы отменён")
                
        except KeyboardInterrupt:
            print("\n👋 Возврат в главное меню...")
        except Exception as e:
            print(f"\n❌ Ошибка при выборе расы: {e}")

    def _handle_load_game(self) -> None:
        """Обработать выбор 'Загрузить игру'."""
        try:
            # Получаем информацию о слотах сохранения
            slots = self._save_game_controller.get_save_slots_info()
            
            # Отображаем меню загрузки
            self._load_game_adapter.display_load_menu(slots)
            
            # Главный цикл меню загрузки
            while True:
                try:
                    choice = self._load_game_adapter.get_user_choice()
                    
                    if choice == "0":
                        break
                    elif choice.isdigit():
                        slot_number = int(choice)
                        if 1 <= slot_number <= 10:
                            # Проверяем слот
                            slot_info = slots[slot_number - 1]
                            if slot_info.is_occupied:
                                # Показываем предпросмотр
                                save_info = slot_info.save_info
                                preview = self._save_game_controller.get_character_preview(
                                    save_info.save_id
                                )
                                
                                if preview:
                                    self._load_game_adapter.display_save_preview(save_info, preview)
                                    
                                    # Подтверждение загрузки
                                    if self._load_game_adapter.confirm_load(save_info):
                                        # Загружаем игру
                                        request = SaveGameRequest(
                                            action="load",
                                            save_id=save_info.save_id
                                        )
                                        
                                        response = self._save_game_controller.handle_request(request)
                                        
                                        if response.success:
                                            self._load_game_adapter.display_success(
                                                f"Игра '{save_info.character_name}' загружена"
                                            )
                                            # Здесь будет переход к игровому процессу
                                            input("Нажмите Enter для продолжения...")
                                            break
                                        else:
                                            self._load_game_adapter.display_error(response.message)
                                            self._load_game_adapter.wait_for_continue()
                                else:
                                    self._load_game_adapter.display_error(
                                        "Не удалось загрузить предпросмотр персонажа"
                                    )
                                    self._load_game_adapter.wait_for_continue()
                            else:
                                self._load_game_adapter.show_slot_empty_message(slot_number)
                        else:
                            self._load_game_adapter.display_error(
                                "Введите номер слота от 1 до 10"
                            )
                            self._load_game_adapter.wait_for_continue()
                    else:
                        self._load_game_adapter.display_error(
                            "Введите номер слота или 0 для выхода"
                        )
                        self._load_game_adapter.wait_for_continue()
                        
                except KeyboardInterrupt:
                    print("\nВозврат в главное меню...")
                    break
                except EOFError:
                    print("\nВозврат в главное меню...")
                    break
                    
        except Exception as e:
            self._welcome_adapter.display_message(
                f"Ошибка в меню загрузки: {str(e)}", 
                "error"
            )

    def _handle_languages(self) -> None:
        """Обработать выбор 'Языки'."""
        try:
            # Показываем меню языков
            print("\n" + "="*50)
            print("LANGUAGES")
            print("="*50)
            print()
            print("1. Русский")
            print("2. English")
            print()
            print("0. Назад в главное меню")
            print("\n" + "-"*30)
            
            # Обрабатываем выбор
            while True:
                try:
                    choice = input("Ваш выбор: ").strip()
                    
                    if choice == "0":
                        break
                    elif choice == "1":
                        self._set_language("ru")
                        break
                    elif choice == "2":
                        self._set_language("en")
                        break
                    else:
                        print("Введите 1 для русского, 2 для английского или 0 для выхода.")
                        
                except KeyboardInterrupt:
                    print("\nВозврат в главное меню...")
                    break
                except EOFError:
                    print("\nВозврат в главное меню...")
                    break
                except Exception as e:
                    print(f"Ошибка: {e}")
                    break
                    
        except Exception as e:
            self._welcome_adapter.display_message(
                f"Ошибка в меню языков: {str(e)}", 
                "error"
            )
        
        input("Нажмите Enter для продолжения...")
    
    def _set_language(self, language_code: str) -> None:
        """Установить язык.
        
        Args:
            language_code: Код языка (ru, en)
        """
        try:
            request = SettingsControllerRequest(
                action="set",
                key="language",
                value=language_code
            )
            
            response = self._settings_controller.handle_request(request)
            
            if response.success:
                language_names = {"ru": "Русский", "en": "English"}
                print(f"\n✅ Язык изменен на {language_names.get(language_code, language_code)}")
            else:
                print(f"\n❌ Ошибка: {response.message}")
                
        except Exception as e:
            print(f"\n❌ Ошибка установки языка: {e}")
    
    def _handle_settings(self) -> None:
        """Обработать выбор 'Настройки'."""
        try:
            # Инициализируем настройки
            settings_response = self._settings_controller.initialize_settings()
            
            if settings_response.success:
                # Показываем меню настроек
                self._show_settings_menu(settings_response)
            else:
                self._welcome_adapter.display_message(
                    f"Ошибка загрузки настроек: {settings_response.message}", 
                    "error"
                )
                
        except Exception as e:
            self._welcome_adapter.display_message(
                f"Ошибка в меню настроек: {str(e)}", 
                "error"
            )
        
        input("Нажмите Enter для продолжения...")

    def _show_settings_menu(self, settings_response) -> None:
        """Показать меню настроек.
        
        Args:
            settings_response: Ответ с настройками
        """
        if not settings_response.all_settings:
            self._welcome_adapter.display_message(
                "Нет доступных настроек", 
                "error"
            )
            return
        
        print("\n" + "="*50)
        print("НАСТРОЙКИ ИГРЫ")
        print("="*50)
        
        for i, setting in enumerate(settings_response.all_settings, 1):
            if setting.setting_type.value == "language":
                current_value = setting.options.get(setting.current_value, setting.current_value)
            else:
                current_value = setting.current_value
            print(f"{i}. {setting.title}: {current_value}")
        
        print("0. Назад в главное меню")
        print("\n" + "-"*30)
        
        # Обрабатываем выбор
        while True:
            try:
                choice = input("Ваш выбор: ").strip()
                
                if choice == "0":
                    break
                elif choice.isdigit():
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(settings_response.all_settings):
                        selected_setting = settings_response.all_settings[choice_num - 1]
                        self._handle_setting_change(selected_setting)
                        break
                    else:
                        print("Неверный выбор. Попробуйте еще раз.")
                else:
                    print("Введите номер пункта меню.")
                    
            except KeyboardInterrupt:
                print("\nВозврат в главное меню...")
                break
            except EOFError:
                print("\nВозврат в главное меню...")
                break
            except Exception as e:
                print(f"Ошибка: {e}")
                break
    
    def _handle_setting_change(self, setting) -> None:
        """Обработать изменение настройки.
        
        Args:
            setting: Изменяемая настройка
        """
        print(f"\nИзменение настройки: {setting.title}")
        print(f"Текущее значение: {setting.current_value}")
        print(f"Описание: {setting.description}")
        
        if setting.setting_type.value == "language":
            print("Доступные варианты:")
            for key, value in setting.options.items():
                current = " (текущий)" if key == setting.current_value else ""
                print(f"  {key}. {value}{current}")
            
            while True:
                try:
                    choice = input("Выберите язык (1-2): ").strip()
                    if choice == "1":
                        new_value = "ru"
                    elif choice == "2":
                        new_value = "en"
                    else:
                        print("Введите 1 для русского или 2 для английского.")
                        continue
                    
                    # Устанавливаем новое значение
                    request = SettingsControllerRequest(
                        action="set",
                        key=setting.key,
                        value=new_value
                    )
                    
                    response = self._settings_controller.handle_request(request)
                    if response.success:
                        print(f"\n✅ Язык изменен на {setting.options.get(new_value, new_value)}")
                        input("Нажмите Enter для продолжения...")
                        break
                    else:
                        print(f"❌ Ошибка: {response.message}")
                        
                except KeyboardInterrupt:
                    print("\nОтмена изменения.")
                    break
        else:
            # Для других типов настроек
            print(f"Введите новое значение (тип: {setting.setting_type.value})")
            if setting.min_value is not None and setting.max_value is not None:
                print(f"Диапазон: {setting.min_value} - {setting.max_value}")
            
            while True:
                try:
                    new_value = input("Новое значение: ").strip()
                    
                    if not new_value:
                        print("Значение не может быть пустым.")
                        continue
                    
                    # Конвертируем значение
                    if setting.setting_type.value == "integer":
                        try:
                            new_value = int(new_value)
                        except ValueError:
                            print("Введите целое число.")
                            continue
                    elif setting.setting_type.value == "boolean":
                        if new_value.lower() in ["true", "1", "да", "yes"]:
                            new_value = True
                        elif new_value.lower() in ["false", "0", "нет", "no"]:
                            new_value = False
                        else:
                            print("Введите true/false, 1/0, да/нет.")
                            continue
                    
                    # Устанавливаем новое значение
                    request = SettingsControllerRequest(
                        action="set",
                        key=setting.key,
                        value=new_value
                    )
                    
                    response = self._settings_controller.handle_request(request)
                    if response.success:
                        print(f"\n✅ Настройка '{setting.title}' обновлена")
                        input("Нажмите Enter для продолжения...")
                        break
                    else:
                        print(f"❌ Ошибка: {response.message}")
                        
                except KeyboardInterrupt:
                    print("\nОтмена изменения.")
                    break
    
    def run(self) -> None:
        """Запустить приложение."""
        try:
            self.run_welcome_screen()
            print("\n🎉 Приложение успешно завершено")

        except KeyboardInterrupt:
            print("\nПриложение прервано пользователем")
        except Exception as error:
            print(f"Критическая ошибка приложения: {error}", file=sys.stderr)
            sys.exit(1)


def main() -> None:
    """Главная функция.
    
    Точка входа с proper dependency injection.
    """
    app = Application()
    app.run()


if __name__ == "__main__":
    main()
