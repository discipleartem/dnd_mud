import yaml
from dataclasses import dataclass
from typing import Dict, Any, Tuple

# Constants
DATABASE_FILE_PATH = 'database.yaml'
WELCOME_MESSAGE = 'Добро пожаловать в текстовую игру по мотивам D&D 5й редакции!'
FILE_NOT_FOUND_ERROR = "Error: The file '{}' was not found."
KEY_ERROR_MESSAGE = "Error: Key '{}' not found in the game database."
INVALID_CHOICE_MESSAGE = "Invalid choice or data error."
NO_AVAILABLE_RACES_MESSAGE = "No available races to display."


def parse_yaml(file_path: str) -> Any:
    """Parse a YAML file and return the data."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except (yaml.YAMLError, OSError) as exc:
        print(f"Error accessing file {file_path}: {exc}")
        return {}


def load_game_database(file_path: str) -> Dict:
    """Load the database from a YAML file."""
    data = parse_yaml(file_path)
    if not data:
        print(FILE_NOT_FOUND_ERROR.format(file_path))
    return data


GAME_DATABASE = load_game_database(DATABASE_FILE_PATH)


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
    def __init__(self):
        if not GAME_DATABASE:
            print("Game cannot be started due to missing or corrupted database.")
            exit(1)
        self.races_dict, self.race_keys = self.build_races_dict()

    def greet_player(self):
        """Print the welcome message."""
        print(WELCOME_MESSAGE)

    def build_races_dict(self) -> Tuple[Dict[int, str], list]:
        """Build the races dictionary from the game database."""
        if 'races' not in GAME_DATABASE:
            print(KEY_ERROR_MESSAGE.format('races'))
            return {}, []
        races = GAME_DATABASE['races']
        races_dict = {index: race['name']['ru'] for index, race in races.items()}
        keys = list(races.keys())
        return races_dict, keys

    def get_user_choice(self) -> int:
        while True:
            try:
                choice = int(input("Please enter your choice: "))
                if self.is_valid_choice(choice):
                    return choice
                else:
                    print(INVALID_CHOICE_MESSAGE)
            except ValueError:
                print(INVALID_CHOICE_MESSAGE)

    def start_game(self):
        """Start the game."""
        self.greet_player()
        if not self.races_dict:
            self.no_races_available()
            return
        self.display_races(self.races_dict)
        user_selection = self.get_user_choice()
        self.process_user_choice(user_selection)

    def process_user_choice(self, user_selection: int):
        """Validate and handle the user's choice."""
        race_key = self.race_keys[user_selection]
        if not self.handle_creature_data(race_key, user_selection):
            self.handle_invalid_choice()

    def no_races_available(self):
        print(NO_AVAILABLE_RACES_MESSAGE)

    def handle_invalid_choice(self):
        print(INVALID_CHOICE_MESSAGE)

    def display_races(self, races_dict: Dict):
        print("Выберите расу:")
        for index, race in races_dict.items():
            print(f"{index}: {race}")

    def is_valid_choice(self, user_selection: int) -> bool:
        return 0 <= user_selection < len(self.race_keys)

    def handle_creature_data(self, race_key: str, user_selection: int) -> bool:
        creature_data = GAME_DATABASE['races'].get(race_key)
        if creature_data is None:
            return False
        self.create_and_display_player(user_selection, creature_data)
        return True

    def create_and_display_player(self, user_choice: int, creature_data: Dict):
        try:
            player = Player(
                race=creature_data['name']['ru'],
                creature_type=creature_data['creature_type']['type'],
                description=creature_data['description'],
                size=creature_data['size'],
                speed=int(creature_data['speed'])
            )
            print(player)
        except (KeyError, TypeError) as exc:
            print(f"An error occurred: {exc}")


# Run the game
if __name__ == "__main__":
    if GAME_DATABASE:
        game_instance = Game()
        game_instance.start_game()
    else:
        print("Game cannot be started due to missing or corrupted database.")