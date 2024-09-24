import os
import yaml
from dataclasses import dataclass
from typing import Dict, Any

# Extracted Constants
DATABASE_FILE_PATH = 'database.yaml'
WELCOME_MESSAGE = 'Добро пожаловать в текстовую игру по мотивам D&D 5й редакции!'
FILE_NOT_FOUND_ERROR = "Error: The file '{}' was not found."
KEY_ERROR_MESSAGE = "Error: Key '{}' not found in the game database."
INVALID_CHOICE_MESSAGE = "Invalid choice or data error."


def parse_yaml(file_path: str) -> Any:
    """Parse a YAML file and return the data."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                return yaml.safe_load(file)
            except yaml.YAMLError as exc:
                print(f"Error parsing YAML file: {exc}")
    except (IOError, OSError) as exc:
        print(f"Error opening file: {exc}")
    return {}


def load_game_database(file_path: str) -> Dict:
    """Load the database from a YAML file."""
    if os.path.isfile(file_path):
        return parse_yaml(file_path)
    else:
        print(FILE_NOT_FOUND_ERROR.format(file_path))
    return {}


GAME_DATA_BASE = load_game_database(DATABASE_FILE_PATH)


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
    def print_welcome_message():
        """Print the welcome message."""
        print(WELCOME_MESSAGE)

    @staticmethod
    def build_races_dict():
        """Build the races dictionary from game database."""
        if 'creature_types' not in GAME_DATA_BASE:
            print(KEY_ERROR_MESSAGE.format('creature_types'))
            return {}, []
        races = GAME_DATA_BASE['creature_types']
        races_dict = {index: value['name']['ru'] for index, (key, value) in enumerate(races.items())}
        keys = list(races.keys())
        return races_dict, keys

    @staticmethod
    def get_user_choice() -> int:
        """Get and return the user's choice, handle input errors."""
        try:
            return int(input())
        except ValueError:
            print(INVALID_CHOICE_MESSAGE)
            return -1

    @staticmethod
    def run_game():
        """Run the game."""
        Game.print_welcome_message()

        races_dict, race_keys = Game.build_races_dict()
        if not races_dict:
            Game.handle_no_races()
            return
        Game.display_races(races_dict)

        user_choice = Game.get_user_choice()
        if not Game.is_valid_choice(user_choice, race_keys):
            Game.handle_invalid_choice()
            return

        chosen_race_key = race_keys[user_choice]
        if not Game.handle_creature_data(chosen_race_key, races_dict, user_choice):
            Game.handle_invalid_choice()

    @staticmethod
    def handle_creature_data(race_key, races_dict, user_choice):
        creature_data = Game.get_creature_data(race_key)
        if creature_data is None:
            return False
        Game.create_and_display_player(races_dict, user_choice, creature_data)
        return True

    @staticmethod
    def handle_no_races():
        print("No available races to display.")

    @staticmethod
    def display_races(races_dict):
        print("Выберите расу:")
        for index, race in races_dict.items():
            print(f"{index}: {race}")

    @staticmethod
    def is_valid_choice(user_choice, race_keys):
        return user_choice in range(len(race_keys))

    @staticmethod
    def handle_invalid_choice():
        print(INVALID_CHOICE_MESSAGE)

    @staticmethod
    def get_creature_data(race_key):
        return GAME_DATA_BASE['creature_types'].get(race_key)

    @staticmethod
    def create_and_display_player(races_dict, user_choice, creature_data):
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
            print(f"An error occurred: {exc}")

# Run the game
if __name__ == "__main__":
    if GAME_DATA_BASE:
        Game.run_game()
    else:
        print("Game cannot be started due to missing or corrupted database.")