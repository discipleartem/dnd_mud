from yaml_parse import log_error, initialize_game_database
from player import Player
from massages import Messages
from typing import Tuple, Dict, Any, Union, List
from dataclasses import dataclass


@dataclass(frozen=True)
class DatabaseKeys:
    RACES: str = 'Races'
    RACE_NAME: str = 'name'
    RU: str = 'ru'


# Initialize game database
game_database = initialize_game_database()


class Game:
    @staticmethod
    def run() -> None:
        """Run the game."""
        Game.greet_and_load_data()

    @staticmethod
    def greet_and_load_data() -> None:
        """Greet the player and load race data."""
        print(Messages.WELCOME)
        available_races, race_keys = Game.load_race_data()
        Game.handle_race_selection(available_races, race_keys)

    @staticmethod
    def load_race_data() -> Tuple[Dict[int, str], List[str]]:
        """Load race data from the game database."""
        if DatabaseKeys.RACES not in game_database:
            log_error(f"Error: Key '{DatabaseKeys.RACES}' not found in the game database.")
            return {}, []
        races = game_database[DatabaseKeys.RACES]
        race_dict = {i: race[DatabaseKeys.RACE_NAME][DatabaseKeys.RU] for i, race in enumerate(races.values())}
        race_keys = list(races.keys())
        return race_dict, race_keys

    @staticmethod
    def show_races(races_dict: Dict[int, str]) -> None:
        """Display the available races."""
        if not races_dict:
            print(Messages.NO_RACES)
            return
        print(Messages.CHOOSE_RACE)
        for index, race in races_dict.items():
            print(f"{index}: {race}")

    @staticmethod
    def get_user_choice() -> int:
        """Get and return the user's choice, handle input errors."""
        try:
            return int(input().strip())
        except ValueError:
            print(Messages.INVALID_CHOICE)
            return -1

    @staticmethod
    def validate_choice(user_choice: int, race_keys: List[str]) -> bool:
        """Check if the user choice is valid."""
        return 0 <= user_choice < len(race_keys)

    @staticmethod
    def fetch_creature_data(race_key: str) -> Union[Dict[str, Any], None]:
        """Get creature data given a race key."""
        return game_database[DatabaseKeys.RACES].get(race_key)

    @staticmethod
    def build_player(races_dict: Dict[int, str], user_choice: int, creature_data: Dict[str, Any]) -> Player:
        """Create a new player instance."""
        return Player(
            race=races_dict[user_choice],
            creature_type=creature_data['creature_type']['type'],
            description=creature_data['description'],
            size=creature_data['size'],
            speed=int(creature_data['speed'])
        )

    @staticmethod
    def show_player_info(player: Player) -> None:
        """Print player information."""
        print(player)

    @staticmethod
    def handle_data_error(exc: Exception) -> None:
        """Handle data-related errors."""
        print(f"{Messages.ERROR_OCCURRED}{exc}")

    @staticmethod
    def process_creature_data(race_key: str, races_dict: Dict[int, str], user_choice: int) -> bool:
        """Handle creature data related actions."""
        creature_data = Game.fetch_creature_data(race_key)
        if not creature_data:
            return False
        try:
            player = Game.build_player(races_dict, user_choice, creature_data)
            Game.show_player_info(player)
        except (KeyError, TypeError) as exc:
            Game.handle_data_error(exc)
            return False
        return True

    @staticmethod
    def handle_user_choice(user_choice: int, race_keys: List[str], races_dict: Dict[int, str]) -> None:
        """Validate user choice and handle accordingly."""
        if not Game.validate_choice(user_choice, race_keys):
            print(Messages.INVALID_CHOICE)
            return
        race_key = race_keys[user_choice]
        if not Game.process_creature_data(race_key, races_dict, user_choice):
            print(Messages.INVALID_CHOICE)

    @staticmethod
    def handle_race_selection(available_races: Dict[int, str], race_keys: List[str]) -> None:
        """Handle the process of race choice."""
        Game.show_races(available_races)
        user_choice = Game.get_user_choice()
        Game.handle_user_choice(user_choice, race_keys, available_races)


# Run the game
if __name__ == "__main__":
    if game_database:
        Game.run()
    else:
        print(Messages.GAME_ERROR)