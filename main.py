from dataclasses import dataclass
from enum import Enum
from typing import Type

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

    @classmethod
    def get_race_translation(cls) -> str:
        translations = {
            Race.HUMAN: 'человек',
            Race.HALF_ORC: 'полу-орк',
            Race.ELF: 'эльф'
        }
        return translations.get(cls.race, cls.race.value)

    @classmethod
    def get_creature_type_translation(cls) -> str:
        return 'гуманоид' if cls.creature_type == CreatureType.HUMANOID else cls.creature_type.value

    @classmethod
    def get_size_translation(cls) -> str:
        size_translations = {
            'tiny': 'крохотный',
            'small': 'маленький',
            'medium': 'средний',
            'large': 'большой',
            'huge': 'огромный'
        }
        return size_translations.get(cls.size, cls.size)


@dataclass
class Human(Creature):
    race: Race = Race.HUMAN
    creature_type: CreatureType = CreatureType.HUMANOID
    size: str = 'medium'
    speed: int = 30
    description: str = HUMAN_DESCRIPTION


@dataclass
class HalfOrc(Creature):
    race: Race = Race.HALF_ORC
    creature_type: CreatureType = CreatureType.HUMANOID
    size: str = 'medium'
    speed: int = 30
    description: str = HALF_ORC_DESCRIPTION


@dataclass
class Elf(Creature):
    race: Race = Race.ELF
    creature_type: CreatureType = CreatureType.HUMANOID
    size: str = 'medium'
    speed: int = 30
    description: str = ELF_DESCRIPTION


@dataclass
class Player(Creature):
    height: int
    weight: int
    eyes: str
    skin: str
    hair: str
    appearance: str
    quenta: str

@dataclass
class SystemMessage:
    __instance__ = None
    wellcome: str = 'Добро пожаловать в игру по мотивам D&D 5e!'
    step_1: str = 'Выберите вашу расу:'

def choose_race() -> Type[Creature]:
    # удаляем класс Player из общего списка
    game_races = [subclass for subclass in Creature.__subclasses__() if subclass.__name__ != 'Player']

    # создаем словарь с индексами и названиями рас {0: 'человек', 1: 'полу-орк', 2: 'эльф'}
    game_races_ru_dict = {index: game_race.get_race_translation() for index, game_race in enumerate(game_races)}
    for index, game_race in enumerate(game_races):
        print()
        print(f"{index}: {game_race.get_race_translation()}")
        print(f"Тип существа: {game_race.get_creature_type_translation()}")
        print(f"Размер: {game_race.get_size_translation()}")
        print(f"Скорость: {game_race.speed} футов")
        wrap_print(f"Описание: {game_race.description}")
    print("Доступные расы:", game_races_ru_dict)
    return game_races[player_choice(game_races_ru_dict)]

def player_choice(choice_dict: dict)-> int:
    pass

class Game:
    __instance__ = None

    @staticmethod
    def run():
        message = SystemMessage()

        #step_0 wellcome
        print(message.wellcome)

        #step_1 choose race
        print(message.step_1)
        game_race = choose_race()



if __name__ == '__main__':
    game = Game()
    game.run()