from yaml_parse import initialize_game_database
from player import Player
from messages import Messages
from errors import ErrorHandler
from typing import Tuple, Dict, Any, Union, List
from dataclasses import dataclass


@dataclass(frozen=True)
class DatabaseKeys:
    RACES: str = 'Races'
    NAME: str = 'name'
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
        Game._load_database()
        Game._start_game()

    @staticmethod
    def _load_database() -> None:
        try:
            Game.database = initialize_game_database()
        except Exception:
            ErrorHandler.log_error_message_static(Messages.DATABASE_LOAD_FAILED)

    @staticmethod
    def _start_game() -> None:
        if Game.database:
            Game._run()
        else:
            print(Messages.GAME_ERROR)

    @staticmethod
    def _run() -> None:
        print(Messages.WELCOME)
        races, race_keys = RaceService.fetch_race_data()
        if races:
            UI.display_race_selection(races, race_keys)


class RaceService:
    @staticmethod
    def fetch_race_data() -> Tuple[Dict[int, str], List[str]]:
        race_data = Game.database.get(DatabaseKeys.RACES)
        if not race_data:
            ErrorHandler.log_key_not_found_error(DatabaseKeys.RACES)
            return {}, []
        race_dict = {i: race[DatabaseKeys.NAME][DatabaseKeys.RU] for i, race in enumerate(race_data.values())}
        return race_dict, list(race_data.keys())

    @staticmethod
    def fetch_creature_details(race_key: str) -> Union[Dict[str, Any], None]:
        return Game.database.get(DatabaseKeys.RACES, {}).get(race_key)

    @staticmethod
    def process_race_selection(race_key: str, race_dict: Dict[int, str], user_choice: int) -> bool:
        creature_data = RaceService.fetch_creature_details(race_key)
        if not creature_data:
            ErrorHandler.log_key_not_found_error(race_key)
            return False
        return RaceService._create_show_player(race_dict, user_choice, creature_data)

    @staticmethod
    def _create_show_player(race_dict: Dict[int, str], user_choice: int, creature_data: Dict[str, Any]) -> bool:
        try:
            player = RaceService._create_player(race_dict[user_choice], creature_data)
            UI.display_player_info(player)
        except (KeyError, TypeError) as e:
            ErrorHandler.handle_error(e)
            return False
        return True

    @staticmethod
    def _create_player(race: str, creature_data: Dict[str, Any]) -> Player:
        details = {
            'creature_type': creature_data[DatabaseKeys.CREATURE_TYPE][DatabaseKeys.TYPE],
            'description': creature_data[DatabaseKeys.DESCRIPTION],
            'size': creature_data[DatabaseKeys.SIZE],
            'speed': int(creature_data[DatabaseKeys.SPEED]),
        }
        return Player(race=race, **details)


class UI:
    @staticmethod
    def display_race_selection(races: Dict[int, str], race_keys: List[str]) -> None:
        if not races:
            print(Messages.NO_RACES)
            return
        print(Messages.CHOOSE_RACE)
        for index, race in races.items():
            print(f"{index}: {race}")
        user_choice = UI.get_user_choice()
        if UI.is_valid_choice(user_choice, race_keys):
            race_key = race_keys[user_choice]
            if not RaceService.process_race_selection(race_key, races, user_choice):
                print(Messages.INVALID_CHOICE)
        else:
            print(Messages.INVALID_CHOICE)

    @staticmethod
    def get_user_choice() -> int:
        try:
            return int(input().strip())
        except ValueError:
            print(Messages.INVALID_CHOICE)
            return -1

    @staticmethod
    def is_valid_choice(choice: int, options: List[str]) -> bool:
        return 0 <= choice < len(options)

    @staticmethod
    def display_player_info(player: Player) -> None:
        print(player)


# Run the game
if __name__ == "__main__":
    Game.initialize()