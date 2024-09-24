import os
import yaml
from typing import Dict, Any, Tuple, Union

DATABASE_FILE_PATH = 'database.yaml'

def parse_yaml(file_path: str) -> Dict[str, Any]:
    """Parse a YAML file and return the data."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except (yaml.YAMLError, IOError, OSError) as exc:
        log_error(f"Error accessing file: {exc}")
    return {}


def load_game_database(file_path: str) -> Dict:
    """Load the database from a YAML file."""
    if os.path.isfile(file_path):
        return parse_yaml(file_path)
    else:
        log_error(f"Error: The file '{file_path}' was not found.")
    return {}


def log_error(message: str) -> None:
    """Handle error by printing a message."""
    print(message)


def initialize_game_database() -> Dict:
    """Initialize and load the game database."""
    return load_game_database(DATABASE_FILE_PATH)