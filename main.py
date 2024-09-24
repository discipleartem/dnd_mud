class Game:
    WELCOME_MESSAGE = 'Добро пожаловать в текстовую игру по мотивам D&D 5й редакции!'

    @staticmethod
    def print_welcome_message():
        print(Game.WELCOME_MESSAGE)

    @staticmethod
    def run_game():
        Game.print_welcome_message()

Game.run_game()

