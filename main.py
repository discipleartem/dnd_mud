from yaml_parse import initialize_game_database
from dataclasses import dataclass

DATABASE = initialize_game_database()


@dataclass
class Creature:
    race :str
    description :str
    creature_type :str
    size :str
    speed :int

@dataclass
class Human(Creature):
    pass



@dataclass
class Orc(Creature):
    pass

@dataclass
class Elf(Creature):
    pass




#Game must run (Singleton)
#Game has Core mechanic
#Game can create Player (Character)
class Game:
    __instance = None


    @staticmethod
    def user_digital_input(race_keys):
        while True:
            user_choice = input("Введите число: ")
            if user_choice.isdigit() and int(user_choice) in range(len(race_keys)):
                return int(user_choice)
            else:
                print("Неверный ввод, введите число в заданном диапазоне")


    @classmethod
    def choose_race(cls):
        print("Выберите расу:")




    @classmethod
    def run(cls):
        #Wellcome screen
        print('Добро пожаловать в текстовую одно-пользовательскую игру по мотивам D&D 5.5 редакции! от 2024 года')

        #choose race
        cls.choose_race()




# Run the game
if __name__ == "__main__":
    Game.run()