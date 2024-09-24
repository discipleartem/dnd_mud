from dataclasses import dataclass
@dataclass(frozen=True)
class Messages:
    WELCOME: str = 'Добро пожаловать в текстовую игру по мотивам D&D 5й редакции!'
    GAME_ERROR: str = "Game cannot be started due to missing or corrupted database."
    CHOOSE_RACE: str = "Выберите расу:"
    INVALID_CHOICE: str = "Invalid choice or data error."
    NO_RACES: str = "No available races to display."
    ERROR_OCCURRED: str = "An error occurred: "