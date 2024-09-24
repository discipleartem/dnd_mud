from yaml_parse import *
from player import Player
from typing import Tuple, Dict, Any, Union, List

# Constants
WELCOME_MESSAGE = 'Добро пожаловать в текстовую игру по мотивам D&D 5й редакции!'
GAME_CANNOT_START_MESSAGE = "Game cannot be started due to missing or corrupted database."
CHOOSE_RACE_MESSAGE = "Выберите расу:"
INVALID_CHOICE_MESSAGE = "Invalid choice or data error."
NO_AVAILABLE_RACES_MESSAGE = "No available races to display."
ERROR_OCCURRED_MESSAGE = "An error occurred: "
RACES_KEY = 'Races'
RACE_NAME_KEY = 'name'
RU_KEY = 'ru'

# Initialize game database
game_database = initialize_game_database()


class Game:
    @staticmethod
    def run() -> None:
        """Run the game."""
        Game.greet_player()
        available_races, race_keys = Game.load_race_data()
        Game.handle_race_selection(available_races, race_keys)

    @staticmethod
    def greet_player() -> None:
        """Print the welcome message."""
        print(WELCOME_MESSAGE)

    @staticmethod
    def load_race_data() -> Tuple[Dict[int, str], List[str]]:
        """Load race data from the game database."""
        if RACES_KEY not in game_database:
            log_error(f"Error: Key '{RACES_KEY}' not found in the game database.")
            return {}, []
        races = game_database[RACES_KEY]
        race_dict = {i: race[RACE_NAME_KEY][RU_KEY] for i, race in enumerate(races.values())}
        race_keys = list(races.keys())
        return race_dict, race_keys

    @staticmethod
    def display_races(races_dict: Dict[int, str]) -> None:
        """Display the available races."""
        if not races_dict:
            print(NO_AVAILABLE_RACES_MESSAGE)
            return
        print(CHOOSE_RACE_MESSAGE)
        for index, race in races_dict.items():
            print(f"{index}: {race}")

    @staticmethod
    def get_user_selection() -> int:
        """Get and return the user's choice, handle input errors."""
        try:
            return int(input().strip())
        except ValueError:
            print(INVALID_CHOICE_MESSAGE)
            return -1

    @staticmethod
    def validate_choice(user_choice: int, race_keys: List[str]) -> bool:
        """Check if the user choice is valid."""
        return 0 <= user_choice < len(race_keys)

    @staticmethod
    def fetch_creature_data(race_key: str) -> Union[Dict[str, Any], None]:
        """Get creature data given a race key."""
        return game_database[RACES_KEY].get(race_key)

    @staticmethod
    def create_player(races_dict: Dict[int, str], user_choice: int, creature_data: Dict[str, Any]) -> Player:
        """Create a new player instance."""
        return Player(
            race=races_dict[user_choice],
            creature_type=creature_data['creature_type']['type'],
            description=creature_data['description'],
            size=creature_data['size'],
            speed=int(creature_data['speed'])
        )

    @staticmethod
    def display_player(player: Player) -> None:
        """Print player information."""
        print(player)

    @staticmethod
    def handle_data_error(exc: Exception) -> None:
        """Handle data-related errors."""
        print(f"{ERROR_OCCURRED_MESSAGE}{exc}")

    @staticmethod
    def process_creature_data(race_key: str, races_dict: Dict[int, str], user_choice: int) -> bool:
        """Handle creature data related actions."""
        creature_data = Game.fetch_creature_data(race_key)
        if not creature_data:
            return False
        try:
            player = Game.create_player(races_dict, user_choice, creature_data)
            Game.display_player(player)
        except (KeyError, TypeError) as exc:
            Game.handle_data_error(exc)
            return False
        return True

    @staticmethod
    def handle_user_choice(user_choice: int, race_keys: List[str], races_dict: Dict[int, str]) -> None:
        """Validate user choice and handle accordingly."""
        if not Game.validate_choice(user_choice, race_keys):
            print(INVALID_CHOICE_MESSAGE)
            return
        race_key = race_keys[user_choice]
        if not Game.process_creature_data(race_key, races_dict, user_choice):
            print(INVALID_CHOICE_MESSAGE)

    @staticmethod
    def handle_race_selection(available_races: Dict[int, str], race_keys: List[str]) -> None:
        """Handle the process of race choice."""
        Game.display_races(available_races)
        user_choice = Game.get_user_selection()
        Game.handle_user_choice(user_choice, race_keys, available_races)


# Run the game
if __name__ == "__main__":
    if game_database:
        Game.run()
    else:
        print(GAME_CANNOT_START_MESSAGE)