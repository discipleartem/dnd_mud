from yaml_parse import initialize_game_database
from dataclasses import dataclass

DATABASE = initialize_game_database()

# Extracting repeated string values as constants
WELCOME_MESSAGE = 'Добро пожаловать в текстовую игру по мотивам D&D 5.5 редакции! от 2024 года'
CHOOSE_RACE_MESSAGE = "Выберите расу:"
RACES_KEY = 'RACES'


@dataclass(frozen=True)
class Messages:
    WELCOME: str = WELCOME_MESSAGE
    CHOOSE_RACE: str = CHOOSE_RACE_MESSAGE


@dataclass
class Creature:
    race: str
    race_name_ru: str
    creature_type: str
    creature_type_name_ru: str
    description: str
    size: str
    size_name_ru: str
    speed: int


# Player must be created from Race
@dataclass
class Player(Creature):
    @staticmethod
    def from_race_data(race_data: dict, race_key: str):
        race_info = race_data[race_key]
        return Player(
            race=race_key,
            race_name_ru=race_info['name']['ru'],
            creature_type=race_info['creature_type']['type'],
            creature_type_name_ru=race_info['creature_type']['name']['ru'],
            description=race_info['description'],
            size=race_info['size']['value'],
            size_name_ru=race_info['size']['name']['ru'],
            speed=race_info['speed']
        )



#Game must run
class Game:

    @staticmethod
    def is_valid_race(race):
        #Проверка наличия ключей, если их нет, то раса не создаётся.
        #['RACES']['name']['ru'] должно быть заполнено
        return race and race.get('name') and race['name'].get('ru')

    @staticmethod
    def create_race_dictionary(races):
        race_dict = {}
        race_keys = []
        for index, (race_key, race_value) in enumerate(races.items()):
            if Game.is_valid_race(race_value):
                race_dict[index] = race_value['name']['ru']
                race_keys.append(race_key)
        return race_dict, race_keys


    def run(self):
        print(Messages.WELCOME)
        print(Messages.CHOOSE_RACE)

        race_dict, race_keys = self.create_race_dictionary(DATABASE[RACES_KEY])
        print(race_dict)

        player_choice = int(input())
        chosen_race_key = race_keys[player_choice]

        player = Player.from_race_data(DATABASE[RACES_KEY], chosen_race_key)
        print(player)


# Run the game
if __name__ == "__main__":
    game_instance = Game()
    game_instance.run()