from dataclasses import dataclass

@dataclass
class Ideology:
    vector: str       # E.g., 'law', 'chaotic', 'neutral'
    name: str         # Full name of the ideology
    short_name: str   # Abbreviated name (e.g., 'lg' for "Lawful Good")
    description: str  # Detailed description of the ideology

# Закон
lawful_good = Ideology(
    vector='law',
    name='Законно-Добрый',
    short_name='lg',
    description=("""существа совершают поступки, считающиеся в обществе как правильные. 
                    Золотые драконы, паладины и большинство дварфов являются законно-добрыми"""
    )
)

lawful_neutral = Ideology(
    vector='law',
    name='Законно-Нейтральный',
    short_name='ln',
    description=("""индивидуумы действуют в соответствии с законом, традицией, или личным кодексом. 
                    Многие монахи и некоторые волшебники являются законно-нейтральными"""
    )
)

lawful_evil = Ideology(
    vector='law',
    name='Законно-Злой',
    short_name='le',
    description=("""существа методично берут то, что хотят, в рамках кодекса традиции, верности, или порядка. 
                    Дьяволы, синие драконы и хоб-гоблины законно-злые."""
    )
)

#Нейтрал
neutral = Ideology(
    vector='neutral',
    name='Нейтральный',
    short_name='n',
    description=("""мировоззрение у тех, кто пред почитает держаться подальше от нравственных вопросов и 
                    не принимать ничью сторону, делая то, что кажется лучшим в данное время. Людоящеры, большинство 
                    друидов и многие люди являются нейтральными."""
    )
)

neutral_good = Ideology(
    vector='neutral',
    name='Нейтрально-Добрый',
    short_name='ng',
    description=("""стараются сделать всё, от них зависящее, чтобы помочь другим. Многие небожители, некоторые 
                    облачные великаны и большинство гномов нейтрально-добрые."""
    )
)

neutral_evil = Ideology(
    vector='neutral',
    name='Нейтрально-Злой',
    short_name='ne',
    description=("""мировоззрение у тех, кто делает всё, что может сойти им с рук, без сострадания и 
                    угрызений совести. Многие дроу, некоторые облачные великаны и юголоты нейтрально-злы."""
    )
)

#Хаос
chaotic_good = Ideology(
    vector='chaotic',
    name='Хаотично-Добрый',
    short_name='ch_g',
    description=("""существа действуют по собственной совести, вне зависимости от того, 
                    что думают другие. Медные драконы, многие эльфы и единороги хаотично-добрые."""
    )
)

chaotic_neutral = Ideology(
    vector='chaotic',
    name='Хаотично-Нейтральный',
    short_name='ch_n',
    description=("""существа следуют своим прихотям, держа свою личную свободу превыше всего. 
                    Многие варвары и разбойники, а также некоторые барды хаотично-нейтральны."""
    )
)

chaotic_evil = Ideology(
    vector='chaotic',
    name='Хаотично-Злой',
    short_name='ch_e',
    description=("""существа действуют со спонтанной жестокостью, вызванной их жадностью, 
                    ненавистью или жаждой крови. Демоны, красные драконы и орки хаотично-злы."""
    )
)


IDEOLOGY = [lawful_good, lawful_neutral, lawful_evil,
            neutral, neutral_good, neutral_evil,
            chaotic_good, chaotic_neutral, chaotic_evil
            ]

IDEOLOGY_DICT = {ideology.short_name: ideology for ideology in IDEOLOGY}
# print(IDEOLOGY_DICT)
#
# for key, ideology in IDEOLOGY_DICT.items():
#     print(f'{key}: {ideology.name}')