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
    description: str
    size: str
    speed: int

@dataclass
class Player(Creature):
    race: str


RACES_KEY = 'RACES' #ключ в котором содержаться все расы

class Game:

    def choose_race(self):
        print(Messages.CHOOSE_RACE)
        race_dict, race_keys = self.create_race_dictionary(DATABASE[RACES_KEY])
        print(race_dict, race_keys)

    @staticmethod
    def create_race_dictionary(races):
        def is_valid_race(race):
            #Проверка наличия ключей, если их нет, то раса не создаеться.
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


    def run(self):
        print(Messages.WELCOME)
        self.choose_race()



# Run the game
if __name__ == "__main__":
    game_instance = Game()
    game_instance.choose_race()