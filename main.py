from dataclasses import dataclass, field
from typing import Optional, Type, Callable, Any
from enum import Enum
from race_descriptions import *
from fix_print_function import wrap_print

class Race(Enum):
    HUMAN = 'human'
    HALF_ORC = 'half-orc'
    ELF = 'elf'


class CreatureType(Enum):
    HUMANOID = 'humanoid'

@dataclass
class Creature:
    name: str
    age: int
    ideology: str

    race: Race
    creature_type: CreatureType
    size: str
    speed: int
    description: str

    def get_race_translation(self) -> str:
        translations = {
            Race.HUMAN: 'человек',
            Race.HALF_ORC: 'полу-орк',
            Race.ELF: 'эльф'
        }
        return translations.get(self.race, self.race.value)

    def get_creature_type_translation(self) -> str:
        return 'гуманоид' if self.creature_type == CreatureType.HUMANOID else self.creature_type.value

    def get_size_translation(self) -> str:
        size_translations = {
            'tiny': 'крохотный',
            'small': 'маленький',
            'medium': 'средний',
            'large': 'большой',
            'huge': 'огромный'
        }
        return size_translations.get(self.size, self.size)


@dataclass
class GameRace(Creature):
    pass


@dataclass
class Human(GameRace):
    race: Race = Race.HUMAN
    creature_type: CreatureType = CreatureType.HUMANOID
    size: str = 'medium'
    speed: int = 30
    description: str = HUMAN_DESCRIPTION


@dataclass
class HalfOrc(GameRace):
    race: Race = Race.HALF_ORC
    creature_type: CreatureType = CreatureType.HUMANOID
    size: str = 'medium'
    speed: int = 30
    description: str = HALF_ORC_DESCRIPTION


@dataclass
class Elf(GameRace):
    race: Race = Race.ELF
    creature_type: CreatureType = CreatureType.HUMANOID
    size: str = 'medium'
    speed: int = 30
    description: str = ELF_DESCRIPTION


@dataclass
class Player(GameRace):
    height: int
    weight: int
    eyes: str
    skin: str
    hair: str
    appearance: str
    quenta: str


def get_user_input(prompt: str, attr_type: Callable, valid_range: Optional[tuple] = None) -> Any:
    """Get validated user input of a specified type."""
    while True:
        user_input = input(prompt)
        try:
            converted_input = attr_type(user_input)
            if valid_range and not (valid_range[0] <= converted_input <= valid_range[1]):
                print(f"Введено неверное значение, должно быть в диапазоне {valid_range}.")
                continue
            return converted_input
        except ValueError:
            print("Неверный ввод, пожалуйста, введите корректное значение.")


def user_digital_input(array: list) -> int:
    while True:
        user_choice = input("Введите число: ")
        if user_choice.isdigit() and 0 <= int(user_choice) < len(array):
            return int(user_choice)
        print("Неверный ввод, введите число в заданном диапазоне")


def get_validated_user_input(prompt: str, attr_type: Callable, valid_range: tuple = None) -> Any:
    while True:
        user_input = input(prompt)
        try:
            converted_input = attr_type(user_input)
            if valid_range and not (valid_range[0] <= converted_input <= valid_range[1]):
                print(f"Введено неверное значение, должно быть в диапазоне {valid_range}.")
                continue
            return converted_input
        except ValueError:
            print("Неверный ввод, пожалуйста, введите корректное значение.")


def get_user_choice(text: str, user_input: str, unit: str,
                    function: Optional[Callable] = None) -> bool:
    """Prompt the user for a yes/no choice."""
    answer = ' '.join(text.split()[1:])
    print(f"{answer} {user_input} {unit} ?")

    choose_dict = {0: 'Нет', 1: 'Да'}
    for key, value in choose_dict.items():
        print(f"{key}: {value}")

    user_choice = get_user_input("Введите номер выбора: ", int, (0, 1))

    if user_choice == 0:
        if function is not None:
            return function()  # Call function if provided
        return False  # Return False if no function is provided
    return user_choice == 1  # Return True if "Да" is chosen
