from yaml_parse import initialize_game_database
from dataclasses import dataclass
from random import randint

DATABASE = initialize_game_database()

# Extracting repeated string values as constants
WELCOME_MESSAGE = 'Добро пожаловать в текстовую игру по мотивам D&D 5.5 редакции! от 2024 года'
CHOOSE_RACE_MESSAGE = "Выберите расу:"
RACES_KEY = 'RACES'


@dataclass(frozen=True)
class Messages:
    WELCOME: str = WELCOME_MESSAGE
    CHOOSE_RACE: str = CHOOSE_RACE_MESSAGE


#Core mechanic can roll dice
@dataclass
class Core:
    @staticmethod
    def roll_d20():
        return randint(1, 20)


@dataclass
class Creature(Core):
    race: str
    race_name_ru: str
    creature_type: str
    creature_type_name_ru: str
    description: str
    size: str
    size_name_ru: str
    speed: int

@dataclass
class Human(Creature):
    #Вы получаете Героическое вдохновение каждый раз после продолжительного отдыха
    """ Героическое вдохновение (resourcefulness)
       Если вы (Персонаж Игрока) имеете Героическое вдохновение, то вы можете потратить его, чтобы
       перебросить любую кость сразу после броска, и вы обязаны использовать новый результат.
       Если вы получаете Героическое вдохновение, но у вас оно уже есть, то оно теряется, если вы
       не передадите его Персонажу Игрока, который не имеет его."""
    resourcefulness :bool
    resourcefulness_name_ru :str
    resourcefulness_description :str

    #Умелость. Вы получаете владение одним навыком на ваш выбор.
    is_skilled  :bool
    is_skilled_description :str

    #Универсальность. Вы получаете черту Происхождения на ваш выбор
    is_universality :bool
    is_universality_description :str

    def is_resourcefulness(self):
        return self.resourcefulness

    def roll_d20(self):
        result = randint(1, 20)
        print(result)
        if self.is_resourcefulness():
            print('Хотите перебросить кубик?')
            print('1 - Да, 0 - Нет')
            if int(input()):
                result = randint(1, 20)
                self.resourcefulness = False
                return result

# @dataclass
# class Skills(Core):
#     # acrobatics: {is_skilled: False, characteristic: dexterity}
#     pass

# Player must be created from Race
# Player can roll dice
@dataclass
class Player(Human):
    pass

#Game must run
#Game has Core mechanic
class Game:

    @classmethod
    def is_valid_race(cls, race):
        #Проверка наличия ключей, если их нет, то раса не создаётся.
        #['RACES']['name']['ru'] должно быть заполнено
        return race and race.get('name') and race['name'].get('ru')

    @classmethod
    def create_race_dictionary(cls, races):
        race_dict = {}
        race_keys = []
        for index, (race_key, race_value) in enumerate(races.items()):
            if Game.is_valid_race(race_value):
                race_dict[index] = race_value['name']['ru']
                race_keys.append(race_key)
        return race_dict, race_keys

    @classmethod
    def create_player(cls, race_key, race_data: dict):
        return Human(
            race=race_key,
            race_name_ru=race_data['name']['ru'],
            creature_type=race_data['creature_type']['type'],
            creature_type_name_ru=race_data['creature_type']['name']['ru'],
            description=race_data['description'],
            size=race_data['size']['value'],
            size_name_ru=race_data['size']['name']['ru'],
            speed=race_data['speed'],
            resourcefulness= True if race_data['race_ability'].get('resourcefulness') else False,
            resourcefulness_name_ru= race_data['race_ability']['resourcefulness']['name']['ru'],
            resourcefulness_description= race_data['race_ability']['resourcefulness']['description'],
            is_skilled= True if race_data['race_ability'].get('skilled') else False,
            is_skilled_description= race_data['race_ability']['skilled']['description'],
            is_universality= True if race_data['race_ability'].get('universality') else False,
            is_universality_description= race_data['race_ability']['universality']['description']
        )


    @classmethod
    def choose_race(cls):
        print(Messages.CHOOSE_RACE)
        race_data = DATABASE[RACES_KEY]
        race_dict, race_keys = cls.create_race_dictionary(race_data)
        print(race_dict)

        chosen_race_index = int(input())
        chosen_race_key = race_keys[chosen_race_index]
        chosen_race_data = race_data[chosen_race_key]
        return chosen_race_key, chosen_race_data

    def run(self):
        #Wellcome screen
        print(Messages.WELCOME)

        #choose race
        race_key, race_data = self.choose_race()

        #create player
        player = self.create_player(race_key, race_data)
        print(player)
        print(player.roll_d20())


# Run the game
if __name__ == "__main__":
    game_instance = Game()
    game_instance.run()