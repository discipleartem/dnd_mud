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


class Game:
    game_database: Dict = {}

    @staticmethod
    def initialize() -> None:
        """Initialize game settings and data."""
        Game.game_database = initialize_game_database()

    @staticmethod
    def run() -> None:
        """Run the game."""
        print(Messages.WELCOME)
        available_races, race_keys = Game.load_race_data()
        if available_races:
            UserInterface.select_race(available_races, race_keys)

    @staticmethod
    def load_race_data() -> Tuple[Dict[int, str], List[str]]:
        """Load race data from the game database."""
        races_data = Game.game_database.get(DatabaseKeys.RACES)
        if not races_data:
            log_error(f"Error: Key '{DatabaseKeys.RACES}' not found in the game database.")
            return {}, []
        return (
            {i: race[DatabaseKeys.RACE_NAME][DatabaseKeys.RU] for i, race in enumerate(races_data.values())},
            list(races_data.keys())
        )

    @staticmethod
    def get_creature_data(race_key: str) -> Union[Dict[str, Any], None]:
        """Get creature data given a race key."""
        return Game.game_database[DatabaseKeys.RACES].get(race_key)

    @staticmethod
    def create_player(race: str, creature_data: Dict[str, Any]) -> Player:
        """Create a new player instance."""
        return Player(
            race=race,
            creature_type=creature_data['creature_type']['type'],
            description=creature_data['description'],
            size=creature_data['size'],
            speed=int(creature_data['speed'])
        )

    @staticmethod
    def process_race_choice(race_key: str, races_dict: Dict[int, str], user_choice: int) -> bool:
        """Handle creature data-related actions."""
        creature_data = Game.get_creature_data(race_key)
        if not creature_data:
            return False
        try:
            player = Game.create_player(races_dict[user_choice], creature_data)
            UserInterface.show_player_info(player)
        except (KeyError, TypeError) as exc:
            UserInterface.handle_error(exc)
            return False
        return True


class UserInterface:
    @staticmethod
    def display_races(races_dict: Dict[int, str]) -> None:
        """Display the available races."""
        if not races_dict:
            print(Messages.NO_RACES)
            return
        print(Messages.CHOOSE_RACE)
        for index, race in races_dict.items():
            print(f"{index}: {race}")

    @staticmethod
    def get_user_input() -> int:
        """Get and return the user's choice, handle input errors."""
        try:
            return int(input().strip())
        except ValueError:
            print(Messages.INVALID_CHOICE)
            return -1

    @staticmethod
    def is_valid_choice(choice: int, options: List[str]) -> bool:
        """Check if the user input is valid."""
        return 0 <= choice < len(options)

    @staticmethod
    def show_player_info(player: Player) -> None:
        """Print player information."""
        print(player)

    @staticmethod
    def handle_error(exc: Exception) -> None:
        """Handle data-related errors."""
        print(f"{Messages.ERROR_OCCURRED}{exc}")

    @staticmethod
    def handle_user_choice(user_choice: int, race_keys: List[str], races_dict: Dict[int, str]) -> None:
        """Validate user choice and handle accordingly."""
        if not UserInterface.is_valid_choice(user_choice, race_keys):
            print(Messages.INVALID_CHOICE)
            return
        race_key = race_keys[user_choice]
        if not Game.process_race_choice(race_key, races_dict, user_choice):
            print(Messages.INVALID_CHOICE)

    @staticmethod
    def select_race(available_races: Dict[int, str], race_keys: List[str]) -> None:
        """Handle the process of race choice."""
        UserInterface.display_races(available_races)
        user_choice = UserInterface.get_user_input()
        UserInterface.handle_user_choice(user_choice, race_keys, available_races)


# Run the game
if __name__ == "__main__":
    Game.initialize()
    if Game.game_database:
        Game.run()
    else:
        print(Messages.GAME_ERROR)