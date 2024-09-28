from yaml_parse import initialize_game_database
from dataclasses import dataclass

DATABASE = initialize_game_database()


@dataclass
class Creature:
    race :str
    race_name_ru :str
    creature_type :str
    creature_type_name_ru :str
    description :str
    size :str
    size_name_ru :str
    speed :int

@dataclass
class Human(Creature):
    #TODO: implement resourcefulness mechanic
    #Вы получаете Героическое вдохновение каждый раз после продолжительного отдыха
    """ Героическое вдохновение (resourcefulness)
       Если вы (Персонаж Игрока) имеете Героическое вдохновение, то вы можете потратить его, чтобы
       перебросить любую кость сразу после броска, и вы обязаны использовать новый результат.
       Если вы получаете Героическое вдохновение, но у вас оно уже есть, то оно теряется, если вы
       не передадите его Персонажу Игрока, который не имеет его."""
    have_resourcefulness :bool
    resourcefulness_name_ru :str
    resourcefulness_description :str

    #TODO: implement skilled mechanic
    #Умелость. Вы получаете владение одним навыком на ваш выбор.
    have_skilled  :bool
    skilled_name_ru: str
    skilled_description :str

    #TODO: implement universality mechanic
    #Универсальность. Вы получаете черту Происхождения на ваш выбор
    have_universality :bool
    universality_description :str



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
    dark_vision_description :str

    #TODO: implement unwavering_fortitude mechanic
    have_unwavering_fortitude :bool
    unwavering_fortitude_name_ru :str
    have_unwavering_fortitude_description :str

@dataclass
class Elf(Creature):
    #TODO: implement dark_vision mechanic
    have_dark_vision :bool
    dark_vision :int
    dark_vision_name_ru :str
    dark_vision_description :str

    #TODO: implement elven_origin mechanic
    elven_origin :bool
    elven_origin_name_ru :str
    elven_origin_description :str

    #TODO: implement legacy_of_fae mechanic
    legacy_of_fae :bool
    legacy_of_fae_name_ru :str
    legacy_of_fae_description :str

    #TODO: implement heightened_senses mechanic
    heightened_senses :bool
    heightened_senses_name_ru :str
    heightened_senses_description :str

    #TODO: implement heightened_senses mechanic
    trance :bool
    trance_name_ru :str
    trance_description :str

@dataclass
class HighElf(Elf):
    sub_race: str
    sub_race_name_ru: str
    sub_race_description: str

    #TODO: implement leveling sub race ability mechanic
    first_lvl :str
    third_lvl :str
    fifth_lvl :str

@dataclass
class DarkElf(Elf):
    sub_race: str
    sub_race_name_ru: str
    sub_race_description: str

    #TODO: implement leveling sub race ability mechanic
    first_lvl :str
    third_lvl :str
    fifth_lvl :str


# Player must be created from Race
@dataclass
class Player:
    @classmethod
    def create_player(cls, race_key, race_data):
        common_attributes = cls.extract_common_attributes(race_data, race_key)
        race_handler = {
            'human': cls.create_human,
            'orc': cls.create_orc,
            'elf': cls.create_elf,
        }
        return race_handler[race_key](common_attributes, race_data)

    @staticmethod
    def extract_common_attributes(data, race_key):
        return {
            'race': race_key,
            'race_name_ru': data['name']['ru'],
            'creature_type': data['creature_type']['type'],
            'creature_type_name_ru': data['creature_type']['name']['ru'],
            'description': data['description'],
            'size': data['size']['value'],
            'size_name_ru': data['size']['name']['ru'],
            'speed': data['speed'],
        }

    @staticmethod
    def create_human(attributes, data):
        return Human(
            **attributes,
            have_resourcefulness='resourcefulness' in data['race_ability'],
            resourcefulness_name_ru=data['race_ability']['resourcefulness']['name']['ru'],
            resourcefulness_description=data['race_ability']['resourcefulness']['description'],
            have_skilled='skilled' in data['race_ability'],
            skilled_name_ru=data['race_ability']['skilled']['name']['ru'],
            skilled_description=data['race_ability']['skilled']['description'],
            have_universality='universality' in data['race_ability'],
            universality_description=data['race_ability']['universality']['description']
        )

    @staticmethod
    def create_orc(attributes, data):
        return Orc(
            **attributes,
            adrenaline_rush='adrenaline_rush' in data['race_ability'],
            adrenaline_rush_name_ru=data['race_ability']['adrenaline_rush']['name']['ru'],
            adrenaline_rush_description=data['race_ability']['adrenaline_rush']['description'],
            have_dark_vision='dark_vision' in data['race_ability'],
            dark_vision=data['race_ability']['dark_vision']['value'],
            dark_vision_name_ru=data['race_ability']['dark_vision']['name']['ru'],
            dark_vision_description=data['race_ability']['dark_vision']['description'],
            have_unwavering_fortitude='unwavering_fortitude' in data['race_ability'],
            unwavering_fortitude_name_ru=data['race_ability']['unwavering_fortitude']['name']['ru'],
            have_unwavering_fortitude_description=data['race_ability']['unwavering_fortitude']['description']
        )

    @staticmethod
    def create_elf(attributes, data):
        elf_attributes = Player.extract_elf_attributes(data)
        sub_race_key = Player.select_elf_sub_race(data)
        creature_attributes = {**attributes, **elf_attributes}
        if sub_race_key == 'high_elf':
            return HighElf(**creature_attributes, **Player.extract_sub_race_attributes(data, sub_race_key))
        if sub_race_key == 'dark_elf':
            return DarkElf(**creature_attributes, **Player.extract_sub_race_attributes(data, sub_race_key))

    @staticmethod
    def select_elf_sub_race(data):
        sub_race_keys = list(data.get('sub_races', {}).keys())
        for i, (sub_race_key, sub_race_data) in enumerate(data['sub_races'].items()):
            print(f"\n{sub_race_data['name']['ru'].capitalize()}\n{sub_race_data['description']}")
            print(f"Особенности подрасы:\nНа 1 уровне: {sub_race_data['first_lvl']}")
            print(f"На 3 уровне: {sub_race_data['third_lvl']}\nНа 5 уровне: {sub_race_data['fifth_lvl']}")

            sub_race_dict, sub_race_keys = Game.create_race_dictionary(data['sub_races'])
            print(f'\n', sub_race_dict)

        user_sub_race_choice = Game.user_digital_input(sub_race_keys)
        return sub_race_keys[user_sub_race_choice]

    @staticmethod
    def extract_elf_attributes(data):
        return {
            'have_dark_vision': 'dark_vision' in data['race_ability'],
            'dark_vision': data['race_ability']['dark_vision']['value'],
            'dark_vision_name_ru': data['race_ability']['dark_vision']['name']['ru'],
            'dark_vision_description': data['race_ability']['dark_vision']['description'],
            'elven_origin': 'elven_origin' in data['race_ability'],
            'elven_origin_name_ru': data['race_ability']['elven_origin']['name']['ru'],
            'elven_origin_description': data['race_ability']['elven_origin']['description'],
            'legacy_of_fae': 'legacy_of_fae' in data['race_ability'],
            'legacy_of_fae_name_ru': data['race_ability']['legacy_of_fae']['name']['ru'],
            'legacy_of_fae_description': data['race_ability']['legacy_of_fae']['description'],
            'heightened_senses': 'heightened_senses' in data['race_ability'],
            'heightened_senses_name_ru': data['race_ability']['heightened_senses']['name']['ru'],
            'heightened_senses_description': data['race_ability']['heightened_senses']['description'],
            'trance': 'trance' in data['race_ability'],
            'trance_name_ru': data['race_ability']['trance']['name']['ru'],
            'trance_description': data['race_ability']['trance']['description']
        }

    @staticmethod
    def extract_sub_race_attributes(data, sub_race_key):
        sub_race_data = data['sub_races'][sub_race_key]
        return {
            'sub_race': sub_race_key,
            'sub_race_name_ru': sub_race_data['name']['ru'],
            'sub_race_description': sub_race_data['description'],
            'first_lvl': sub_race_data.get('first_lvl'),
            'third_lvl': sub_race_data.get('third_lvl'),
            'fifth_lvl': sub_race_data.get('fifth_lvl')
        }


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

        for race in race_data:
            print(race_data[race]['name']['ru'].capitalize())
            print(race_data[race]['description'])
            print('Расовые особенности:')

            for ability in race_data[race]['race_ability']:
                print(race_data[race]['race_ability'][ability]['name']['ru'].capitalize() + ': ')
                print(race_data[race]['race_ability'][ability]['description'])
                print()
            print()

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
        player = Player.create_player(race_key, race_data)
        print(player)



# Run the game
if __name__ == "__main__":
    game_instance = Game()
    game_instance.run()