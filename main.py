import os
import yaml
from dataclasses import dataclass
from typing import Dict, Any

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
    except (yaml.YAMLError, IOError, OSError) as exc:
        print(f"Error accessing file: {exc}")
    return {}


def load_game_database(file_path: str) -> Dict:
    """Load the database from a YAML file."""
    if os.path.isfile(file_path):
        return parse_yaml(file_path)
    else:
        print(FILE_NOT_FOUND_ERROR.format(file_path))
    return {}


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

    @staticmethod
    def greet_player():
        """Print the welcome message."""
        print(WELCOME_MESSAGE)

    @staticmethod
    def display_message(message: str):
        """Display a generic message."""
        print(message)

    @staticmethod
    def build_races_dict():
        """Build the races dictionary from the game database."""
        if 'Races' not in GAME_DATABASE:
            Game.display_message(KEY_ERROR_MESSAGE.format('Races'))
            return {}, []

        races = GAME_DATABASE['Races']
        races_dict = {index: value['name']['ru'] for index, (key, value) in enumerate(races.items())}
        keys = list(races.keys())
        return races_dict, keys

    @staticmethod
    def display_races(races_dict: Dict[int, str]):
        """Display the available races."""
        print("Выберите расу:")
        for index, race in races_dict.items():
            print(f"{index}: {race}")

    @staticmethod
    def get_user_choice() -> int:
        """Get and return the user's choice, handle input errors."""
        try:
            return int(input())
        except ValueError:
            Game.display_message(INVALID_CHOICE_MESSAGE)
            return -1

    @staticmethod
    def is_valid_choice(user_choice: int, race_keys: list) -> bool:
        """Check if the user's choice is valid."""
        return 0 <= user_choice < len(race_keys)

    @staticmethod
    def get_creature_data(race_key: str) -> Dict:
        """Get creature data given a race key."""
        return GAME_DATABASE['Races'].get(race_key)

    @staticmethod
    def create_and_display_player(races_dict: Dict[int, str], user_choice: int, creature_data: Dict):
        """Create and display player information."""
        try:
            player = Player(
                race=races_dict[user_choice],
                creature_type=creature_data['creature_type']['type'],
                description=creature_data['description'],
                size=creature_data['size'],
                speed=int(creature_data['speed'])
            )
            print(player)
        except (KeyError, TypeError) as exc:
            Game.display_message(f"An error occurred: {exc}")

    @staticmethod
    def handle_creature_data(race_key: str, races_dict: Dict[int, str], user_choice: int) -> bool:
        """Handle creature data related actions."""
        creature_data = Game.get_creature_data(race_key)
        if creature_data is None:
            return False

        Game.create_and_display_player(races_dict, user_choice, creature_data)
        return True

    @staticmethod
    def validate_and_handle_choice(user_choice: int, race_keys: list, races_dict: Dict[int, str]) -> bool:
        """Validate user choice and handle accordingly."""
        if not Game.is_valid_choice(user_choice, race_keys):
            return False

        race_key = race_keys[user_choice]
        return Game.handle_creature_data(race_key, races_dict, user_choice)

    @staticmethod
    def run_game():
        """Run the game."""
        Game.greet_player()
        races_dict, race_keys = Game.build_races_dict()
        if not races_dict:
            Game.display_message(NO_AVAILABLE_RACES_MESSAGE)
            return

        Game.display_races(races_dict)
        user_choice = Game.get_user_choice()
        if not Game.validate_and_handle_choice(user_choice, race_keys, races_dict):
            Game.display_message(INVALID_CHOICE_MESSAGE)


# Run the game
if __name__ == "__main__":
    if GAME_DATABASE:
        Game.run_game()
    else:
        print("Game cannot be started due to missing or corrupted database.")