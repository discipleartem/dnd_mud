"""Консольный адаптер для ввода имени персонажа."""

from src.models.entities.character import Character
from src.services.name_input_service import NameInputService


class NameInputAdapter:
    """Консольный адаптер для ввода имени персонажа.

    Применяемые паттерны:
    - Adapter (Адаптер) — адаптирует сервис для консольного интерфейса
    - Template Method (Шаблонный метод) — определяет алгоритм взаимодействия

    Применяемые принципы:
    - Single Responsibility — только консольное взаимодействие
    - User Experience — понятные сообщения и обработка ошибок
    - Separation of Concerns — логика отделена от представления
    """

    def __init__(self, name_input_service: NameInputService):
        """Инициализировать адаптер с сервисом ввода имени.

        Args:
            name_input_service: Сервис для бизнес-логики ввода имени
        """
        self.service = name_input_service

    def prompt_for_name(self) -> Character | None:
        """Запросить имя у пользователя и создать персонажа.

        Returns:
            Созданный персонаж или None если пользователь отменил ввод
        """
        print("\n" + "=" * 50)
        print("СОЗДАНИЕ ПЕРСОНАЖА")
        print("=" * 50)
        print("\nШАГ 1: ВВОД ИМЕНИ")
        print()

        while True:
            try:
                # Запрос имени
                name = input("Введите имя персонажа: ").strip()

                # Проверка на отмену
                if name.lower() in ["отмена", "cancel", "exit", "выход"]:
                    print("\nСоздание персонажа отменено.")
                    return None

                if not name:
                    print("Имя не может быть пустым. Попробуйте еще раз.")
                    continue

                # Попытка создания персонажа
                character = self.service.create_character_with_name(name)

                # Успешное создание
                print(f"\nПерсонаж '{character.name}' успешно создан!")
                print(f"ID: {character.id}")
                created_at_str = (
                    character.created_at.strftime("%d.%m.%Y %H:%M")
                    if character.created_at
                    else "неизвестно"
                )
                print(f"Создан: {created_at_str}")
                print()

                return character

            except ValueError as e:
                # Обработка ошибок валидации
                print(f"\nОшибка: {e}")
                print("Пожалуйста, попробуйте другое имя.")
                print()

            except KeyboardInterrupt:
                # Обработка прерывания пользователем
                print("\n\nСоздание персонажа отменено пользователем.")
                return None

            except Exception as e:
                # Обработка непредвиденных ошибок
                print(f"\nПроизошла непредвиденная ошибка: {e}")
                print("Пожалуйста, попробуйте еще раз.")
                print()

    def show_success_message(self, character: Character) -> None:
        """Показать сообщение об успешном создании персонажа.

        Args:
            character: Созданный персонаж
        """
        print(
            f"\nПоздравляем! Персонаж '{character.name}' готов к приключениям!"
        )
        print("Персонаж сохранен в файл data/characters.json")
        print(f"ID: {character.id}")
        created_at_str = (
            character.created_at.strftime("%d.%m.%Y %H:%M")
            if character.created_at
            else "неизвестно"
        )
        print(f"Создан: {created_at_str}")
        print("Теперь вы можете продолжить настройку персонажа...")
        print()

    def show_cancellation_message(self) -> None:
        """Показать сообщение об отмене создания персонажа."""
        print("\nСоздание персонажа отменено.")
        print(
            "Вы можете вернуться к этому позже через меню 'Создать персонажа'."
        )
        print()
