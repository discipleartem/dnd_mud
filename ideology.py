# -*- coding: utf-8 -*-

LAW = 'law'
NEUTRAL = 'neutral'
CHAOTIC = 'chaotic'

LAWFUL_GOOD = 'lawful-good'
LAWFUL_NEUTRAL = 'lawful-neutral'
LAWFUL_EVIL = 'lawful-evil'

NEUTRAL_GOOD = 'neutral-good'
NEUTRAL_EVIL = 'neutral-evil'

CHAOTIC_GOOD = 'chaotic-good'
CHAOTIC_NEUTRAL = 'chaotic-neutral'
CHAOTIC_EVIL = 'chaotic-evil'

LG = 'lg'
LN = 'ln'
LE = 'le'

N = 'n'
NG = 'ng'
NE = 'ne'

CH_G = 'ch_g'
CH_N = 'ch_n'
CH_E = 'ch_e'

class Ideology:
    __instance = None

    def __init__(self, vector: str, name: str, short_name: str, description: str):
        self.vector = vector       # E.g., 'law', 'chaotic', 'neutral'
        self.name = name           # Full name of the ideology
        self.short_name = short_name  # Abbreviated name (e.g., 'lg' for "Lawful Good")
        self.description = description  # Detailed description of the ideology


    def get_translation(self, translation_type: str) -> str:
        translations = {
            'vector': {
                LAW: 'закон',
                NEUTRAL: 'нейтральное',
                CHAOTIC: 'хаос'
            },
            'name': {
                LAWFUL_GOOD: 'законно-добрый',
                LAWFUL_NEUTRAL: 'законно-нейтральный',
                LAWFUL_EVIL: 'законно-злой',
                NEUTRAL: 'нейтральный',
                NEUTRAL_GOOD: 'нейтрально-добрый',
                NEUTRAL_EVIL: 'нейтрально-злой',
                CHAOTIC_GOOD: 'хаотично-добрый',
                CHAOTIC_NEUTRAL: 'хаотично-нейтральный',
                CHAOTIC_EVIL: 'хаотично-злой'
            },
            'short_name': {
                LG: 'зд',
                LN: 'зн',
                LE: 'зз',
                N: 'н',
                NG: 'нд',
                NE: 'нз',
                CH_G: 'хд',
                CH_N: 'хн',
                CH_E: 'хз',
            }
        }
        return translations[translation_type].get(getattr(self, translation_type), getattr(self, translation_type))


    def get_vector_translation(self) -> str:
        return self.get_translation('vector')


    def get_name_translation(self) -> str:
        return self.get_translation('name')


    def get_short_name_translation(self) -> str:
        return self.get_translation('short_name')
# Закон
lawful_good = Ideology(
    vector=LAW,
    name=LAWFUL_GOOD,
    short_name=LG,
    description="""существа совершают поступки, считающиеся в обществе как правильные. Золотые драконы, """
                """паладины и большинство дварфов являются законно-добрыми"""
)

lawful_neutral = Ideology(
    vector=LAW,
    name=LAWFUL_NEUTRAL,
    short_name=LN,
    description="""индивидуумы действуют в соответствии с законом, традицией, или личным кодексом."""
                """ Многие монахи и некоторые волшебники являются законно-нейтральными"""
)

lawful_evil = Ideology(
    vector=LAW,
    name=LAWFUL_EVIL,
    short_name=LE,
    description="""существа методично берут то, что хотят, в рамках кодекса традиции, верности,""" 
                """ или порядка. Дьяволы, синие драконы и хоб-гоблины законно-злые."""
)

#Нейтрал
neutral = Ideology(
    vector=NEUTRAL,
    name=NEUTRAL,
    short_name=N,
    description="""мировоззрение у тех, кто пред почитает держаться подальше от нравственных вопросов и """
                """не принимать ничью сторону, делая то, что кажется лучшим в данное время. Людоящеры, """
                """большинство друидов и многие люди являются нейтральными."""
)

neutral_good = Ideology(
    vector=NEUTRAL,
    name=NEUTRAL_GOOD,
    short_name=NG,
    description="""стараются сделать всё, от них зависящее, чтобы помочь другим. Многие небожители, """
                """некоторые облачные великаны и большинство гномов нейтрально-добрые."""
)

neutral_evil = Ideology(
    vector=NEUTRAL,
    name=NEUTRAL_EVIL,
    short_name=NE,
    description="""мировоззрение у тех, кто делает всё, что может сойти им с рук, без сострадания и """
                """угрызений совести. Многие дроу, некоторые облачные великаны и юголоты нейтрально-злы."""
)

#Хаос
chaotic_good = Ideology(
    vector=CHAOTIC,
    name=CHAOTIC_GOOD,
    short_name=CH_G,
    description="""существа действуют по собственной совести, вне зависимости от того, что думают другие. """
                """Медные драконы, многие эльфы и единороги хаотично-добрые."""
)

chaotic_neutral = Ideology(
    vector=CHAOTIC,
    name=CHAOTIC_NEUTRAL,
    short_name=CH_N,
    description="""существа следуют своим прихотям, держа свою личную свободу превыше всего. Многие варвары и """
                """разбойники,а также некоторые барды хаотично-нейтральны."""
)

chaotic_evil = Ideology(
    vector=CHAOTIC,
    name=CHAOTIC_EVIL,
    short_name=CH_E,
    description="""существа действуют со спонтанной жестокостью, вызванной их жадностью, ненавистью или жаждой крови. """
                """Демоны, красные драконы и орки хаотично-злы."""
)


IDEOLOGY = [lawful_good, lawful_neutral, lawful_evil,
            neutral, neutral_good, neutral_evil,
            chaotic_good, chaotic_neutral, chaotic_evil
            ]

IDEOLOGY_DICT = {ideology.short_name: ideology for ideology in IDEOLOGY}
