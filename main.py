from yaml_parse import *
from player import Player

# Constants
WELCOME_MESSAGE = 'Добро пожаловать в текстовую игру по мотивам D&D 5й редакции!'
GAME_CANNOT_START_MESSAGE = "Game cannot be started due to missing or corrupted database."
CHOOSE_RACE_MESSAGE = "Выберите расу:"
INVALID_CHOICE_MESSAGE = "Invalid choice or data error."

game_database = initialize_game_database()


class Game:
    @staticmethod
    def greet_player() -> None:
        """Print the welcome message."""
        print(WELCOME_MESSAGE)

    @staticmethod
    def get_race_data() -> Tuple[Dict[int, str], list]:
        """Fetch and return race data."""
        if 'Races' not in game_database:
            log_error("Error: Key 'Races' not found in the game database.")
            return {}, []
        races = game_database['Races']
        races_dict = {index: value['name']['ru'] for index, (key, value) in enumerate(races.items())}
        keys = list(races.keys())
        return races_dict, keys

    @staticmethod
    def display_races(races_dict: Dict[int, str]) -> None:
        """Display the available races."""
        print(CHOOSE_RACE_MESSAGE)
        for index, race in races_dict.items():
            print(f"{index}: {race}")

    @staticmethod
    def get_user_selection() -> int:
        """Get and return the user's choice, handle input errors."""
        try:
            return int(input())
        except ValueError:
            print(INVALID_CHOICE_MESSAGE)
            return -1

    @staticmethod
    def validate_choice(user_choice: int, race_keys: list) -> bool:
        """Check if the user choice is valid."""
        return 0 <= user_choice < len(race_keys)

    @staticmethod
    def fetch_creature_data(race_key: str) -> Union[Dict[str, Any], None]:
        """Get creature data given a race key."""
        return game_database['Races'].get(race_key)

    @staticmethod
    def create_player_instance(races_dict: Dict[int, str], user_choice: int, creature_data: Dict[str, Any]) -> Player:
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
    def process_creature_data(race_key: str, races_dict: Dict[int, str], user_choice: int) -> bool:
        """Handle creature data related actions."""
        creature_data = Game.fetch_creature_data(race_key)
        if creature_data is None:
            return False
        try:
            player = Game.create_player_instance(races_dict, user_choice, creature_data)
            Game.display_player(player)
        except (KeyError, TypeError) as exc:
            print(f"An error occurred: {exc}")
        return True

    @staticmethod
    def process_user_choice(user_choice: int, race_keys: list, races_dict: Dict[int, str]) -> bool:
        """Validate user choice and handle accordingly."""
        if not Game.validate_choice(user_choice, race_keys):
            return False
        race_key = race_keys[user_choice]
        return Game.process_creature_data(race_key, races_dict, user_choice)

    @staticmethod
    def choose_race(available_races: Dict[int, str], race_keys: list) -> None:
        """Handle the process of race choice."""
        if not available_races:
            print("No available races to display.")
        else:
            Game.display_races(available_races)
            user_choice = Game.get_user_selection()
            if not Game.process_user_choice(user_choice, race_keys, available_races):
                print(INVALID_CHOICE_MESSAGE)

    @staticmethod
    def run() -> None:
        """Run the game."""
        Game.greet_player()
        available_races, race_keys = Game.get_race_data()
        Game.choose_race(available_races, race_keys)


# Run the game
if __name__ == "__main__":
    if game_database:
        Game.run()
    else:
        print(GAME_CANNOT_START_MESSAGE)