from dataclasses import dataclass
from typing import Type, Callable, Optional, Any
from race_descriptions import *
from fix_print_function import wrap_print



@dataclass
class Creature:
    name: str
    age: int
    ideology: str
    creature_type: str
    size: str
    race: str
    speed: int
    description: str

    @classmethod
    def get_creature_type_translation(cls) -> str:
        if cls.creature_type == 'humanoid':
            return 'гуманоид'
        else:
            cls.creature_type

class GameRace(Creature):
    age_range: tuple[int, int]
    creature_type: str = 'humanoid'
    size: str = 'medium'

    @classmethod
    def get_race_translation(cls) -> str:
        translations = {
            'human': 'человек',
            'half-orc': 'полу-орк',
            'elf': 'эльф'
        }
        return translations.get(cls.race, cls.race)



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
    race: str = 'human'
    speed: int = 30
    description: str = HUMAN_DESCRIPTION
    age_range: tuple = (18, 100)


@dataclass
class HalfOrc(GameRace):
    race: str = 'half-orc'
    speed: int = 30
    description: str = HALF_ORC_DESCRIPTION
    age_range: tuple = (14, 75)

@dataclass
class Elf(GameRace):
    race: str = 'elf'
    speed: int = 30
    description: str = ELF_DESCRIPTION
    age_range: tuple = (100, 750)

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


def choose_race() -> Type[GameRace]:
    # Динамически получаем все подклассы GameRace
    game_races = GameRace.__subclasses__()
    print(game_races)

    # создаем словарь с индексами и названиями рас {0: 'человек', 1: 'полу-орк', 2: 'эльф'}
    game_races_ru_dict = {index: game_race.get_race_translation() for index, game_race in enumerate(game_races)}
    for index, game_race in enumerate(game_races):
        print(f"\n{index}: {game_race.get_race_translation()}")
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

#проверка ввода пользователя
def validate_user_choice(question: str, value: Any, expected_type: type,
                         callback: Optional[Callable]) -> Any:
    while True:
        if isinstance(value, expected_type):
            print(f"{' '.join(question.split()[1:])} {value} ?")

            #подтверждение выбора
            if user_confirm(callback=callback):
                return value


#создаем имя персонажа
def create_player_name() -> str:
    text = "Введите имя игрока: "
    while True:
        player_name = input(text).strip()
        if player_name:  # Проверяем, что имя не пустое
            #валидируем имя
            return validate_user_choice(question=text, value=player_name, expected_type=str,
                                        callback=create_player_name)
        else:
            print("Имя не может быть пустым. Пожалуйста, введите имя.")

#создаем возраст игрока
def create_player_age(age_range: tuple) -> int:
    text = "Введите возраст игрока: "
    while True:
        player_age = input(text).strip()
        try:
            player_age = int(player_age)
            if player_age in range(age_range[0], age_range[1] + 1):
                confirmed_age = validate_user_choice(question=text, value=player_age, expected_type=int,
                                            callback=lambda: create_player_age(age_range))
                return confirmed_age
            else:
                print(f"Вы ввели неверный возраст. Пожалуйста, введите возраст "
                      f"в диапазоне от {age_range[0]} до {age_range[1]} лет.")
        except ValueError:
            print("Вы ввели неверное значение. Пожалуйста, введите возраст числом.")

def create_player(game_race: Type[GameRace]) -> Player:
    player = Player(
        name=create_player_name(),
        age=create_player_age(age_range=game_race.age_range),
        ideology=input("Введите идеологию: "),

        creature_type=game_race.creature_type,
        size=game_race.size,
        race=game_race.race,
        speed=game_race.speed,
        description=game_race.description,

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
