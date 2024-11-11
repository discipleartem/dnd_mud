from dataclasses import dataclass
from enum import Enum
from typing import Type, Callable, Optional, Any

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
    ideology: str
    age: int

    race: Race
    creature_type: CreatureType
    size: str
    speed: int
    description: str


class GameRace(Creature):

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
        }
        return size_translations.get(cls.size, cls.size)


@dataclass
class Human(GameRace):
    age: int = range(18, 100)
    race: Race = Race.HUMAN
    creature_type: CreatureType = CreatureType.HUMANOID
    size: str = 'medium'
    speed: int = 30
    description: str = HUMAN_DESCRIPTION


@dataclass
class HalfOrc(GameRace):
    age: int = range(14, 75)
    race: Race = Race.HALF_ORC
    creature_type: CreatureType = CreatureType.HUMANOID
    size: str = 'medium'
    speed: int = 30
    description: str = HALF_ORC_DESCRIPTION


@dataclass
class Elf(GameRace):
    age: int = range(100, 750)
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
    # Динамически получаем все подклассы GameRace
    game_races = GameRace.__subclasses__()
    print(game_races)

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


def player_choice(choice_dict: dict) -> int:
    while True:
        user_choice = input("Сделайте свой выбор: ")
        try:
            user_choice = int(user_choice)
            if user_choice in choice_dict.keys():
                return user_choice
        except ValueError:
            print("Вы ввели неверное значение. Попробуйте еще раз.")

def user_confirm(callback: Optional[Callable]) -> bool:
    options = {0: 'нет', 1: 'да'}
    while True:
        choice = input(f"Выберите {options}: ")
        try:
            choice = int(choice)
            if choice == 1:
                return True
            elif choice == 0:
                return callback()
        except ValueError:
            print("Вы ввели неверное значение. Попробуйте еще раз.")


def validate_user_choice(question: str, value: Any, expected_type: type,
                         callback: Optional[Callable]) -> Any:
    while True:
        if isinstance(value, expected_type):
            print(f"{' '.join(question.split()[1:])} {value} ?")
            if user_confirm(callback=callback):
                return value
        else:
            callback()



def create_player_name() -> str:
    text = "Введите имя игрока: "
    while True:
        player_name = input(text).strip()
        if player_name:  # Проверяем, что имя не пустое
            return validate_user_choice(question=text, value=player_name, expected_type=str,
                                        callback=create_player_name)
        else:
            print("Имя не может быть пустым. Пожалуйста, введите имя.")


def create_player(race: Type[GameRace]) -> Player:
    player = Player(
        name=create_player_name(),
        ideology=input("Введите идеологию: "),
        age=int(input("Введите возраст: ")),

        race=race.race,
        creature_type=race.creature_type,
        size=race.size,
        speed=race.speed,
        description=race.description,

        height=int(input("Введите рост: ")),
        weight=int(input("Введите вес: ")),
        eyes=input("Введите цвет глаз: "),
        skin=input("Введите цвет кожи: "),
        hair=input("Введите цвет волос: "),
        appearance=input("Введите внешний вид: "),
        quenta=input("Введите краткое описание: ")
    )
    return player


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

        #step_2 create player
        player = create_player(game_race)
        print(player)


if __name__ == '__main__':
    game = Game()
    game.run()
