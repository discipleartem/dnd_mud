from yaml_parse import initialize_game_database
from dataclasses import dataclass


DATABASE = initialize_game_database()

@dataclass(frozen=True)
class Messages:
    WELCOME: str = 'Добро пожаловать в текстовую игру по мотивам D&D 5.5 редакции! от 2024 года'
    CHOOSE_RACE: str = "Выберите расу:"

@dataclass
class Creature:
    creature_type: str
    creature_type_name_ru :str

    description: str

    size: str
    size_name_ru: str

    speed: int

@dataclass
class Player(Creature):
    race: str
    race_name_ru: str


RACES_KEY = 'RACES' #ключ в котором содержаться все расы

class Game:

    @staticmethod
    def create_race_dictionary(races):
        def is_valid_race(race):
            #Проверка наличия ключей, если их нет, то раса не создаеться.
            # ['RACES']['name']['ru'] должно быть заполнено
            return race and race.get('name') and race['name'].get('ru')

        race_dict = {}
        race_keys = []
        next_index = 0

        for race_key, race_value in races.items():
            if is_valid_race(race_value):
                race_dict[next_index] = race_value['name']['ru']
                race_keys.append(race_key)
                next_index += 1

        return race_dict, race_keys

    @staticmethod
    def create_player_from_race(race_data, race_key):
        return Player(
            creature_type=race_data[race_key]['creature_type']['type'],
            creature_type_name_ru=race_data[race_key]['creature_type']['name']['ru'],
            description=race_data[race_key]['description'],
            size=race_data[race_key]['size']['value'],
            size_name_ru=race_data[race_key]['size']['name']['ru'],
            speed=race_data[race_key]['speed'],
            race=race_key,
            race_name_ru=race_data[race_key]['name']['ru']
        )


    def run(self):
        print(Messages.WELCOME)
        print(Messages.CHOOSE_RACE)

        race_dict, race_keys = self.create_race_dictionary(DATABASE[RACES_KEY])
        print(race_dict)

        player_choice = int(input())
        chosen_race_key = race_keys[player_choice]

        player = self.create_player_from_race(DATABASE[RACES_KEY], chosen_race_key)
        print(player)





# Run the game
if __name__ == "__main__":
    game_instance = Game()
    game_instance.run()