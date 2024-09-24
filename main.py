import os
import yaml  # Using PyYAML for YAML parsing


def parse_yaml(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            data = yaml.safe_load(file)
        except yaml.YAMLError as exc:
            print(f"Error parsing YAML file: {exc}")
            return {}
    return data


def make_db():
    file_path = 'database.yaml'
    if os.path.isfile(file_path):
        return parse_yaml(file_path)
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