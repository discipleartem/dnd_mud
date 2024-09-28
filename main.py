from yaml_parse import initialize_game_database
from dataclasses import dataclass

DATABASE = initialize_game_database()


#Core mechanic can roll dice
# @dataclass
# class Core:
#     @classmethod
#     def roll_d20(cls):
#         return randint(1, 20)


@dataclass
class Creature:
    race: str
    race_name_ru: str
    creature_type: str
    creature_type_name_ru: str
    description: str
    size: str
    size_name_ru: str
    speed: int

@dataclass
class Human(Creature):
    #Вы получаете Героическое вдохновение каждый раз после продолжительного отдыха
    """ Героическое вдохновение (resourcefulness)
       Если вы (Персонаж Игрока) имеете Героическое вдохновение, то вы можете потратить его, чтобы
       перебросить любую кость сразу после броска, и вы обязаны использовать новый результат.
       Если вы получаете Героическое вдохновение, но у вас оно уже есть, то оно теряется, если вы
       не передадите его Персонажу Игрока, который не имеет его."""
    have_resourcefulness :bool
    resourcefulness_name_ru :str
    resourcefulness_description :str

    #Умелость. Вы получаете владение одним навыком на ваш выбор.
    have_skilled  :bool
    skilled_name_ru: str
    skilled_description :str

    #Универсальность. Вы получаете черту Происхождения на ваш выбор
    have_universality :bool
    universality_description :str


    # def roll_d20(self):
    #     result = randint(1, 20)
    #     print(result)
    #     if self.is_resourcefulness():
    #         print('Хотите перебросить кубик?')
    #         print('1 - Да, 0 - Нет')
    #         if int(input()):
    #             result = randint(1, 20)
    #             self.resourcefulness = False
    #             return result

@dataclass
class Orc(Creature):
    #TODO: implement adrenaline_rush mechanic
    adrenaline_rush :bool
    adrenaline_rush_name_ru :str
    adrenaline_rush_description :str

    #TODO: implement dark_vision mechanic
    have_dark_vision :bool
    dark_vision :int
    dark_vision_name_ru :str
    have_dark_vision_description :str

    #TODO: implement unwavering_fortitude mechanic
    have_unwavering_fortitude :bool
    unwavering_fortitude_name_ru :str
    have_unwavering_fortitude_description :str

# @dataclass
# class Skills(Core):
#     # acrobatics: {is_skilled: False, characteristic: dexterity}
#     pass

# Player must be created from Race
@dataclass
class Player(Human,Orc):
    pass

#Game must run
#Game has Core mechanic
#Game can create Player
class Game:

    @classmethod
    def is_valid_race(cls, race):
        #Проверка наличия ключей, если их нет, то раса не создаётся.
        #['RACES']['name']['ru'] должно быть заполнено
        return race and race.get('name') and race['name'].get('ru')

    @classmethod
    def create_race_dictionary(cls, races):
        race_dict = {}
        race_keys = []
        for index, (race_key, race_value) in enumerate(races.items()):
            if Game.is_valid_race(race_value):
                race_dict[index] = race_value['name']['ru']
                race_keys.append(race_key)
        return race_dict, race_keys

    @classmethod
    def create_player(cls, race_key, race_data: dict):
        while True:
            if race_key == 'human':
                return Human(
                    race= race_key,
                    race_name_ru= race_data['name']['ru'],
                    creature_type= race_data['creature_type']['type'],
                    creature_type_name_ru= race_data['creature_type']['name']['ru'],
                    description= race_data['description'],
                    size= race_data['size']['value'],
                    size_name_ru= race_data['size']['name']['ru'],
                    speed= race_data['speed'],

                    have_resourcefulness= True if race_data['race_ability'].get('resourcefulness') else False,
                    resourcefulness_name_ru= race_data['race_ability']['resourcefulness']['name']['ru'],
                    resourcefulness_description= race_data['race_ability']['resourcefulness']['description'],

                    have_skilled= True if race_data['race_ability'].get('skilled') else False,
                    skilled_name_ru= race_data['race_ability']['skilled']['name']['ru'],
                    skilled_description= race_data['race_ability']['skilled']['description'],
                    have_universality= True if race_data['race_ability'].get('universality') else False,
                    universality_description= race_data['race_ability']['universality']['description']
                )
            if race_key == 'orc':
                return Orc(
                    race=race_key,
                    race_name_ru=race_data['name']['ru'],
                    creature_type=race_data['creature_type']['type'],
                    creature_type_name_ru=race_data['creature_type']['name']['ru'],
                    description=race_data['description'],
                    size=race_data['size']['value'],
                    size_name_ru=race_data['size']['name']['ru'],
                    speed=race_data['speed'],

                    adrenaline_rush= True if race_data['race_ability'].get('adrenaline_rush') else False,
                    adrenaline_rush_name_ru= race_data['race_ability']['adrenaline_rush']['name']['ru'],
                    adrenaline_rush_description= race_data['race_ability']['adrenaline_rush']['description'],

                    have_dark_vision= True if race_data['race_ability'].get('dark_vision') else False,
                    dark_vision= race_data['race_ability']['dark_vision']['value'],
                    dark_vision_name_ru= race_data['race_ability']['dark_vision']['name']['ru'],
                    have_dark_vision_description= race_data['race_ability']['dark_vision']['description'],

                    have_unwavering_fortitude= True if race_data['race_ability'].get('unwavering_fortitude') else False,
                    unwavering_fortitude_name_ru= race_data['race_ability']['unwavering_fortitude']['name']['ru'],
                    have_unwavering_fortitude_description= race_data['race_ability']['unwavering_fortitude']['description']
                )
            else:
                print('Неверный выбор расы (отсутствует в БД)')

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
        race_data = DATABASE['RACES']
        race_dict, race_keys = cls.create_race_dictionary(race_data)
        print(race_dict)

        chosen_race_index = cls.user_digital_input(race_keys)

        chosen_race_key = race_keys[chosen_race_index]
        chosen_race_data = race_data[chosen_race_key]
        return chosen_race_key, chosen_race_data



    def run(self):
        #Wellcome screen
        print('Добро пожаловать в текстовую игру по мотивам D&D 5.5 редакции! от 2024 года')

        #choose race
        race_key, race_data = self.choose_race()

        #create player
        player = self.create_player(race_key, race_data)
        print(player)



# Run the game
if __name__ == "__main__":
    game_instance = Game()
    game_instance.run()