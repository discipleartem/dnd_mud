import os
import yaml  # Using PyYAML for YAML parsing
from dataclasses import dataclass
from typing import Dict, Any

# Extracted Constants
DATABASE_FILE_PATH = 'database.yaml'
WELCOME_MESSAGE = 'Добро пожаловать в текстовую игру по мотивам D&D 5й редакции!'


def parse_yaml(file_path: str) -> Any:
    """Parse a YAML file and return the data."""
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            data = yaml.safe_load(file)
        except yaml.YAMLError as exc:
            print(f"Error parsing YAML file: {exc}")
            return {}
    return data


def load_database(file_path: str) -> Dict:
    """Load the database from a YAML file."""
    if os.path.isfile(file_path):
        return parse_yaml(file_path)
    else:
        print(f"Error: The file '{file_path}' was not found.")
        return {}


# Inline the function call directly into the constant
GAME_DATA_BASE = load_database(DATABASE_FILE_PATH)


@dataclass
class Creature:
    creature_type: Dict[str, Dict[str, str]]
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
            print("Error: Key 'creature_types' not found in the game database.")
            return {}, []

        races = GAME_DATA_BASE['creature_types']
        races_dict = {index: value['name']['ru'] for index, (key, value) in enumerate(races.items())}
        keys = list(races.keys())

        return races_dict, keys

    @staticmethod
    def run_game():
        """Run the game."""
        Game.print_welcome_message()

        races_dict, keys = Game.build_races_dict()

        if not races_dict:
            print("No available races to display.")
            return

        print("Выберите расу:")
        for index, race in races_dict.items():
            print(f"{index}: {race}")

        try:
            user_choice = int(input())
            chosen_race_key = keys[user_choice]
            creature_data = GAME_DATA_BASE['creature_types'][chosen_race_key]
            player = Player(
                race= races_dict[user_choice],
                creature_type=creature_data['creature_type']['type'],
                description=creature_data['description'],
                size=creature_data['size'],
                speed=creature_data['speed']
            )
            print(player)
        except (ValueError, IndexError, KeyError):
            print("Invalid choice or data error.")


# Run the game
if __name__ == "__main__":
    if GAME_DATA_BASE:
        Game.run_game()
    else:
        print("Game cannot be started due to missing or corrupted database.")
