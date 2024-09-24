import os
import yaml  # Using PyYAML for YAML parsing

# Extracted Constants
DATABASE_FILE_PATH = 'database.yaml'
WELCOME_MESSAGE = 'Добро пожаловать в текстовую игру по мотивам D&D 5й редакции!'


def parse_yaml(file_path):
    """Parse a YAML file and return the data."""
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            data = yaml.safe_load(file)
        except yaml.YAMLError as exc:
            print(f"Error parsing YAML file: {exc}")
            return {}
    return data


def load_database(file_path):
    """Load the database from a YAML file."""
    if os.path.isfile(file_path):
        return parse_yaml(file_path)
    else:
        print(f"Error: The file '{file_path}' was not found.")
        return {}


# Inline the function call directly into the constant
GAME_DATA_BASE = load_database(DATABASE_FILE_PATH)


class Game:
    @staticmethod
    def print_welcome_message():
        """Print the welcome message."""
        print(WELCOME_MESSAGE)

    @staticmethod
    def run_game():
        """Run the game."""
        Game.print_welcome_message()


# Run the game
Game.run_game()