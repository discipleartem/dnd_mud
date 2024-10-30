from dataclasses import dataclass, field
from typing import Optional, Type, Callable
from race_descriptions import *
from fix_print_function import wrap_print


@dataclass
class Creature:
    name: str
    age: int
    ideology: str

    race: str
    creature_type: str
    size: str
    speed: int
    description: str

    @classmethod
    def get_race_translation(cls) -> str:
        translations = {
            'human': 'человек',
            'half-orc': 'полу-орк',
            'elf': 'эльф'
        }
        return translations.get(cls.race, cls.race)

    @classmethod
    def get_creature_type_translation(cls) -> str:
        return 'гуманоид' if cls.creature_type == 'humanoid' else cls.creature_type

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
class GameRace(Creature):
    pass


@dataclass
class Human(GameRace):
    race: str = 'human'
    creature_type: str = 'humanoid'
    size: str = 'medium'
    speed: int = 30
    description: str = HUMAN_DESCRIPTION


@dataclass
class HalfOrc(GameRace):
    race: str = 'half-orc'
    creature_type: str = 'humanoid'
    size: str = 'medium'
    speed: int = 30
    description: str = HALF_ORC_DESCRIPTION


@dataclass
class Elf(GameRace):
    race: str = 'elf'
    creature_type: str = 'humanoid'
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



def user_digital_input(array: list) -> int:
    while True:
        user_choice = input("Введите число: ")
        if user_choice.isdigit() and 0 <= int(user_choice) < len(array):
            return int(user_choice)
        print("Неверный ввод, введите число в заданном диапазоне")


def get_user_choice(text: str, user_input: str, unit: str, function: Optional[Callable] = None) -> bool:
    answer = ' '.join(text.split()[1:])
    print(f"{answer} {user_input} {unit} ?")

    choose_dict = {0: 'Нет', 1: 'Да'}
    print(choose_dict)

    user_choice = user_digital_input(array=list(choose_dict.values()))

    # Проверка, была ли передана функция
    if user_choice == 0 and function is not None:
        return function()  # Вызов функции, если она передана
    else:
        return user_choice == 1  # Возвращаем True, если выбрано "Да"



def create_player_attributes(text: str, attr_type: type):
    while True:
        print(text)
        user_input = input()
        if isinstance(user_input, attr_type):
            answer = ' '.join(text.split()[1:])
            print(f"{answer}: {user_input} ?")
            choose_dict = {0: 'Нет', 1: 'Да'}
            print(choose_dict)

            user_choice = user_digital_input(array=list(choose_dict.values()))
            if user_choice == 1:
                return user_input
            else:
                print("Введено неверное значение")

def create_player_height_attributes(text: str, attr_type: type, race: str):
    if race in ['человек', 'эльф', 'полу-орк']:
        wrap_print(f"Для расы {race}: рост отдельного представителя может составлять от 5 до 6 футов")
        print(text)

    while True:
        user_input = input()

        try:
            converted_input = attr_type(user_input)
        except ValueError:
            print("Неверный ввод, пожалуйста, введите число.")
            continue  # Запрашиваем ввод снова

        if 5 <= converted_input <= 6:
            if get_user_choice(text=text, user_input=user_input, unit='футов'):
                               # function=create_player_height_attributes(text, attr_type, race)):
                return converted_input
        else:
            print("Введено неверное значение")


def create_player_weight_attributes(text: str, attr_type: type, race: str):
    while True:
        print(text)
        weight_ranges = {
            'человек': (125, 250),
            'полу-орк': (180, 250),
            'эльф': (100, 145)
        }

        if race in weight_ranges:
            min_weight, max_weight = weight_ranges[race]
            wrap_print(f"для расы {race}: вес — от {min_weight} до {max_weight} фунтов: ")
            user_input = input()
            converted_input = attr_type(user_input)

            if converted_input and min_weight <= converted_input <= max_weight:
                if get_user_choice(text=text, user_input=user_input, unit='фунтов'):
                    return converted_input
                else:
                    print("Введено неверное значение")




def create_player_optional_attributes(text: str, attr_type: type):
    while True:
        print("Пожалуйста, введите только одно слово.")
        print(text)

        user_input = input()
        converted_input = attr_type(user_input)

        # Проверяем, что введенное значение не содержит пробелов
        if converted_input and  " " not in user_input:
            if get_user_choice(text, user_input, unit=''):
                return user_input
            else:
                print("Введено неверное значение")

def create_player_age_attribute(text: str, attr_type: type, race: str):
    age_ranges: dict = {
        'человек': (18, 100),
        'полу-орк': (14, 75),
        'эльф': (100, 750)
    }

    if race not in age_ranges:
        print("Неизвестная раса.")
        return None

    min_age, max_age = age_ranges[race]

    while True:
        wrap_print(f"для расы {race}: возраст — от {min_age} до {max_age} лет: ")
        user_input = input()
        converted_input = attr_type(user_input)
        if converted_input and min_age <= converted_input <= max_age:
            if get_user_choice(text=text, user_input=user_input, unit='лет'):
                return converted_input
        else:
            print("Введено неверное значение. Пожалуйста, попробуйте снова.")


def create_player(selected_race):
    player_name = create_player_optional_attributes(text="Введите имя вашего персонажа: ", attr_type=str)
    player_age = create_player_age_attribute(text="Введите возраст вашего персонажа: ",
                                                    attr_type=int, race=selected_race.get_race_translation())

    player_height = create_player_height_attributes(text="Введите рост вашего персонажа: ",
                                             attr_type=int, race = selected_race.get_race_translation())

    player_weight = create_player_weight_attributes(text="Введите вес вашего персонажа: ", attr_type=int, race = selected_race.get_race_translation())
    player_eyes = create_player_optional_attributes(text="Введите цвет глаз вашего персонажа: ", attr_type=str)


    player_skin = create_player_optional_attributes(text="Введите цвет кожи вашего персонажа: ", attr_type=str)
    player_hair = create_player_optional_attributes(text="Введите цвет волос вашего персонажа: ", attr_type=str)




    player_appearance = input("Введите описание внешности вашего персонажа: ")
    player_quenta = input("Введите краткую историю вашего персонажа: ")
    player_ideology = input("Введите идеологию вашего персонажа: ")

    player = Player(
        name=player_name,
        age=player_age,
        ideology=player_ideology,

        race=selected_race.race,
        creature_type=selected_race.creature_type,
        size=selected_race.size,
        speed=selected_race.speed,
        description=selected_race.description,

        height=player_height,
        weight=player_weight,
        eyes=player_eyes,
        skin=player_skin,
        hair=player_hair,
        appearance=player_appearance,
        quenta=player_quenta
    )
    return player

def describe_game_races(game_races= list[Type[GameRace]]) -> None:
    for index, game_race in enumerate(game_races):
        print()
        print(f"{index}: {game_race.get_race_translation()}")
        print(f"Тип существа: {game_race.get_creature_type_translation()}")
        print(f"Размер: {game_race.get_size_translation()}")
        print(f"Скорость: {game_race.speed} футов")
        wrap_print(f"Описание: {game_race.description}")


def choose_race():
    print("Выберите расу:")

    # удаляем класс Player из общего списка
    game_races = [subclass for subclass in GameRace.__subclasses__() if subclass.__name__ != 'Player']
    print(game_races)


    # Создаем словарь, ключи — имена рас, значения — объекты класса GameRace
    game_races_ru_dict = {index: game_race.get_race_translation() for index, game_race in enumerate(game_races)}

    # Выводим описание всех рас
    describe_game_races(game_races=game_races)
    print(game_races_ru_dict)

    user_race_choice = user_digital_input(list(game_races_ru_dict.values()))

    # Выбираем расу
    selected_race = next(game_race for game_race in game_races if game_race.get_race_translation() == game_races_ru_dict[user_race_choice])

    player = create_player(selected_race)
    print(player.__dict__)
    print(dir(player))




@dataclass
class Game:
    race: GameRace = field(init=False)


    @classmethod
    def run(cls):
        print('Добро пожаловать в текстовую одно-пользовательскую игру по мотивам D&D 5 редакции!')
        choose_race()


# Run the game
if __name__ == "__main__":
    game = Game()
    game.run()