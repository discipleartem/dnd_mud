from dataclasses import dataclass, field
from typing import Type, Callable, Optional, Any
from race_descriptions import *
from ideology import IDEOLOGY_DICT, Ideology
from fix_print_function import wrap_print

@dataclass
class Attribute:
    name: str
    description: str
    value: int

@dataclass
class Creature:
    name: str #1
    age: int #2
    ideology: Ideology #3

    race_name: str #4
    speed: int #5
    description: str #6

    creature_type: str #7
    size: str #8

    strength: Attribute = field(default_factory=lambda:
                                Attribute(name="Сила", description="Физическая сила и мощь.", value=10))  # 9
    dexterity: Attribute = field(default_factory=lambda:
                                Attribute(name="Ловкость", description="Гибкость и рефлексы.", value=10))  # 10
    constitution: Attribute = field(default_factory=lambda:
                            Attribute(name="Телосложение", description="Здоровье и выносливость.", value=10))  # 11
    intelligence: Attribute = field(default_factory=lambda:
                        Attribute(name="Интеллект", description="Умственные способности и логика.", value=10))  # 12
    wisdom: Attribute = field(default_factory=lambda:
                                    Attribute(name="Мудрость", description="Восприятие и интуиция.", value=10))  # 13
    charisma: Attribute = field(default_factory=lambda:
                                Attribute(name="Харизма", description="Влияние и социальные навыки.", value=10))  # 14



    @classmethod
    def get_creature_type_translation(cls) -> str:
        if cls.creature_type == 'humanoid':
            return 'гуманоид'
        else:
            return cls.creature_type


@dataclass
class GameRace(Creature):
    creature_type: str = 'humanoid' #7
    size: str = 'medium' #8

    #добавил Optional, чтобы не было ошибок при создании экземпляра (нарушен порядок наследования параметров)
    age_range: Optional[tuple[int, int]] = None    #9 доп
    specificity: Optional[str] = None #10 доп

    @classmethod
    def get_race_name_translation(cls) -> str:
        translations = {
            'human': 'человек',
            'half-orc': 'полу-орк',
            'high-elf': 'высший эльф'
        }
        return translations.get(cls.race_name, cls.race_name)



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
    race_name: str = 'human'  # 4
    speed: int = 30  # 5
    description: str = HUMAN_DESCRIPTION  # 6
    age_range: tuple = (18, 100)  # 9 доп

    #TODO добавить атрибуты и механику для "особенностей расы"
    specificity: str = HUMAN_SPECIFICITY  # 10 доп


@dataclass
class HalfOrc(GameRace):
    race_name: str = 'half-orc'  # 4
    speed: int = 30  # 5
    description: str = HALF_ORC_DESCRIPTION  # 6
    age_range: tuple = (14, 75)  # 9 доп

    # TODO добавить атрибуты и механику для "особенностей расы"
    specificity: str = HALF_ORC_SPECIFICITY  # 10 доп

@dataclass
class HighElf(GameRace):
    race_name: str = 'high-elf'  # 4
    speed: int = 30  # 5
    description: str = ELF_DESCRIPTION  # 6
    age_range: tuple = (100, 750)  # 9 доп

    # TODO добавить атрибуты и механику для "особенностей расы"
    specificity: str = ELF_SPECIFICITY  # 10 доп


@dataclass
class Character:
    race: Type[GameRace]
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

    # создаем словарь с индексами и названиями рас {0: 'человек', 1: 'полу-орк', 2: 'эльф'}
    game_races_ru_dict = {index: game_race.get_race_name_translation() for index, game_race in enumerate(game_races)}
    for index, game_race in enumerate(game_races):

        print(f"\n{index}: {game_race.get_race_name_translation()}")
        print(f"Тип существа: {game_race.get_creature_type_translation()}")
        print(f"Размер: {game_race.get_size_translation()}")
        print(f"Скорость: {game_race.speed} футов")
        print()
        wrap_print(f"Описание: {game_race.description}")
        print()
        print(f"Особенности расы: {game_race.specificity}")
        print("===============================================================")


    print("Доступные расы:", game_races_ru_dict)
    chosen_index = player_choice(choice_dict=game_races_ru_dict)
    return game_races[chosen_index]


def player_choice(choice_dict: dict) -> int:
    while True:
        try:
            user_choice = input("Сделайте свой выбор: ")
            user_choice = int(user_choice)
            if user_choice in choice_dict.keys():
                return user_choice
            else:
                print(f"Выберите значение из {choice_dict.keys()}.")
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
        else:
            print(f"Вы ввели неверное значение. Пожалуйста, введите {expected_type.__name__}.")


#создаем имя персонажа
def create_player_name() -> str:
    text = "Введите имя игрока: "
    while True:
        player_name = input(text).strip()  # убираем пробелы в начале и в конце
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

#выбор мировоззрение игрока
def create_player_ideology() -> Ideology:

    print('Выберите ваше мировоззрение: ')
    for key, ideology in IDEOLOGY_DICT.items():
        print(f'короткая запись: {key}')
        print(f'название: {ideology.get_name_translation().title()}')
        print(f'направление: {ideology.get_vector_translation().capitalize()}')
        wrap_print(f'Описание: {ideology.description}')
        print()

    while True:
        text = "Выберите мировоззрение (короткая запись): "
        player_ideology = input(text).strip()

        if player_ideology in IDEOLOGY_DICT.keys():
            user_choice = validate_user_choice(question=text,
                                               value=player_ideology,
                                               expected_type=str,
                                               callback=create_player_ideology)
            return IDEOLOGY_DICT[user_choice]

        else:
            print("Вы ввели неверное значение. Введите короткую запись.")



def create_player(game_race: Type[GameRace.__subclasses__()], player_class) -> Character:
    # Создаем экземпляр выбранной расы
    race_instance = game_race(
        name=create_player_name(),
        age=create_player_age(game_race.age_range),
        ideology=create_player_ideology()
    )

    player = player_class(race=race_instance,
                      height=int(input("Введите рост игрока: ")),
                      weight=int(input("Введите вес игрока: ")),
                      eyes=input("Введите цвет глаз игрока: "),
                      skin=input("Введите цвет кожи игрока: "),
                      hair=input("Введите цвет волос игрока: "),
                      appearance=input("Введите внешность игрока: "),
                      quenta=input("Введите предысторию игрока: ")
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
        race = choose_race()

        #step_2 create player
        player = create_player(game_race=race, player_class= Character)
        print(player)


if __name__ == '__main__':
    game = Game()
    game.run()
