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


class Game:
    @staticmethod
    def run():
        print(Messages.WELCOME)

# Run the game
if __name__ == "__main__":
    Game.run()