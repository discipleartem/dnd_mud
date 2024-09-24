import os

def parse_yaml(file_path):
    data = {}
    with open(file_path, 'r') as file:
        for line in file:
            key, value = line.strip().split(': ')
            data[key] = value
    return data

def make_db():
    file_path = 'database.yaml'
    if os.path.isfile(file_path):
        xls = parse_yaml(file_path)
        return xls
    else:
        print(f"Error: The file '{file_path}' was not found.")
        return {}


GAME_DATA_BASE = make_db()


class Game:
    WELCOME_MESSAGE = 'Добро пожаловать в текстовую игру по мотивам D&D 5й редакции!'

    @staticmethod
    def print_welcome_message():
        print(Game.WELCOME_MESSAGE)

    @staticmethod
    def run_game():
        Game.print_welcome_message()


Game.run_game()