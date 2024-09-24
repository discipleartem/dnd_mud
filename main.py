from yaml_parse import log_error, initialize_game_database
from player import Player
from massages import Messages, INVALID_CHOICE
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
        Game.load_database()

    @staticmethod
    def load_database() -> None:
        Game.game_database = initialize_game_database()

    @staticmethod
    def run() -> None:
        """Run the game."""
        print(Messages.WELCOME)
        races, race_keys = Game._get_race_data()
        if races:
            UserInterface.select_race(races, race_keys)

    @staticmethod
    def _get_race_data() -> Tuple[Dict[int, str], List[str]]:
        """Load race data from the game database."""
        races_data = Game._get_races()
        if not races_data:
            log_error(f"Error: Key '{DatabaseKeys.RACES}' not found in the game database.")
            return {}, []
        race_dict = Game._create_race_dict(races_data)
        race_keys = list(races_data.keys())
        return race_dict, race_keys

    @staticmethod
    def _create_race_dict(races_data: Dict[str, Any]) -> Dict[int, str]:
        """Create race dictionary from races data."""
        return {i: race[DatabaseKeys.RACE_NAME][DatabaseKeys.RU] for i, race in enumerate(races_data.values())}

    @staticmethod
    def _get_races() -> Dict[str, Any]:
        """Get races from the game database."""
        return Game.game_database.get(DatabaseKeys.RACES, {})

    @staticmethod
    def _get_creature_details(race_key: str) -> Union[Dict[str, Any], None]:
        """Get creature details given a race key."""
        return Game.game_database.get(DatabaseKeys.RACES, {}).get(race_key)

    @staticmethod
    def _create_player_instance(race: str, creature_data: Dict[str, Any]) -> Player:
        """Create a new player instance."""
        return Player(
            race=race,
            creature_type=creature_data['creature_type']['type'],
            description=creature_data['description'],
            size=creature_data['size'],
            speed=int(creature_data['speed'])
        )

    @staticmethod
    def handle_race_choice(race_key: str, race_dict: Dict[int, str], user_choice: int) -> bool:
        """Process the race choice made by the user."""
        creature_data = Game._get_creature_details(race_key)
        if not creature_data:
            return False
        try:
            player = Game._create_player_instance(race_dict[user_choice], creature_data)
            UserInterface.show_player_info(player)
        except (KeyError, TypeError) as e:
            UserInterface.handle_error(e)
            return False
        return True


class UserInterface:
    @staticmethod
    def display_races(races: Dict[int, str]) -> None:
        """Display the available races."""
        if not races:
            print(Messages.NO_RACES)
            return
        print(Messages.CHOOSE_RACE)
        for index, race in races.items():
            print(f"{index}: {race}")

    @staticmethod
    def get_user_choice() -> int:
        """Get and return the user's choice, handling input errors."""
        try:
            return int(input().strip())
        except ValueError:
            print(Messages.INVALID_CHOICE)
            return INVALID_CHOICE

    @staticmethod
    def is_valid_choice(choice: int, options: List[str]) -> bool:
        """Check if the user input is valid."""
        return 0 <= choice < len(options)

    @staticmethod
    def show_player_info(player: Player) -> None:
        """Print player information."""
        print(player)

    @staticmethod
    def handle_error(e: Exception) -> None:
        """Handle data-related errors."""
        print(f"{Messages.ERROR_OCCURRED}{e}")

    @staticmethod
    def process_user_choice(user_choice: int, race_keys: List[str], races: Dict[int, str]) -> None:
        """Validate user choice and process accordingly."""
        if UserInterface.is_valid_choice(user_choice, race_keys):
            race_key = race_keys[user_choice]
            if not Game.handle_race_choice(race_key, races, user_choice):
                print(Messages.INVALID_CHOICE)
        else:
            print(Messages.INVALID_CHOICE)

    @staticmethod
    def select_race(races: Dict[int, str], race_keys: List[str]) -> None:
        """Handle the race selection process."""
        UserInterface.display_races(races)
        user_choice = UserInterface.get_user_choice()
        UserInterface.process_user_choice(user_choice, race_keys, races)


# Run the game
if __name__ == "__main__":
    Game.initialize()
    if Game.game_database:
        Game.run()
    else:
        print(Messages.GAME_ERROR)