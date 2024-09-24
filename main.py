from yaml_parse import initialize_game_database, log_error
from player import Player
from massages import Messages, INVALID_CHOICE
from typing import Tuple, Dict, Any, Union, List
from dataclasses import dataclass


@dataclass(frozen=True)
class GameDatabaseKeys:
    RACES_KEY: str = 'Races'
    RACE_NAME: str = 'name'
    CREATURE_TYPE: str = 'creature_type'
    TYPE: str = 'type'
    DESCRIPTION: str = 'description'
    SIZE: str = 'size'
    SPEED: str = 'speed'
    RU: str = 'ru'


class Game:
    database: Dict = {}

    @staticmethod
    def initialize() -> None:
        """Initialize game settings and data."""
        Game.load_database()

    @staticmethod
    def load_database() -> None:
        Game.database = initialize_game_database()

    @staticmethod
    def run() -> None:
        """Run the game."""
        print(Messages.WELCOME)
        races, race_keys = RaceHandler.get_race_data()
        if races:
            UserInterface.select_race(races, race_keys)

    @staticmethod
    def log_error(message: str) -> None:
        """Log an error message."""
        log_error(message)


@dataclass
class RaceHandler:
    @staticmethod
    def get_race_data() -> Tuple[Dict[int, str], List[str]]:
        """Load race data from the game database."""
        race_data = Game.database.get(GameDatabaseKeys.RACES_KEY)
        if not race_data:
            Game.log_error(f"Error: Key '{GameDatabaseKeys.RACES_KEY}' not found in the game database.")
            return {}, []
        race_dict = RaceHandler.parse_race_data(race_data)
        return race_dict, list(race_data.keys())

    @staticmethod
    def parse_race_data(race_data: Dict[str, Any]) -> Dict[int, str]:
        """Construct a dictionary of races."""
        return {
            i: race[GameDatabaseKeys.RACE_NAME][GameDatabaseKeys.RU]
            for i, race in enumerate(race_data.values())
        }

    @staticmethod
    def get_creature_details(race_key: str) -> Union[Dict[str, Any], None]:
        """Get creature details given a race key."""
        return Game.database.get(GameDatabaseKeys.RACES_KEY, {}).get(race_key)

    @staticmethod
    def handle_race_choice(race_key: str, race_dict: Dict[int, str], user_choice: int) -> bool:
        """Process the race choice made by the user."""
        creature_data = RaceHandler.get_creature_details(race_key)
        if not creature_data:
            return False
        try:
            player = RaceHandler.create_player_instance(race_dict[user_choice], creature_data)
            UserInterface.show_player_info(player)
        except (KeyError, TypeError) as e:
            UserInterface.handle_error(e)
            return False
        return True

    @staticmethod
    def create_player_instance(race: str, creature_data: Dict[str, Any]) -> Player:
        """Create a new player instance."""
        return Player(
            race=race,
            creature_type=creature_data[GameDatabaseKeys.CREATURE_TYPE][GameDatabaseKeys.TYPE],
            description=creature_data[GameDatabaseKeys.DESCRIPTION],
            size=creature_data[GameDatabaseKeys.SIZE],
            speed=int(creature_data[GameDatabaseKeys.SPEED])
        )


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
            if not RaceHandler.handle_race_choice(race_key, races, user_choice):
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
    if Game.database:
        Game.run()
    else:
        print(Messages.GAME_ERROR)