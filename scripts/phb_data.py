#!/usr/bin/env python3
"""Константы и маппинги PHB для генерации docs/rules/."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EntityRef:
    """Ссылка на сущность PHB."""

    id: str
    ru_name: str
    pages: tuple[int, int]
    mud_status: str
    yaml_ref: str | None = None


RACES: tuple[EntityRef, ...] = (
    EntityRef(
        "dwarf",
        "Дварф",
        (18, 20),
        "partial",
        "database/races/races.yaml#dwarf",
    ),
    EntityRef(
        "elf", "Эльф", (21, 25), "partial", "database/races/races.yaml#elf"
    ),
    EntityRef("halfling", "Полурослик", (26, 28), "planned"),
    EntityRef(
        "human",
        "Человек",
        (29, 31),
        "partial",
        "database/races/races.yaml#human",
    ),
    EntityRef("dragonborn", "Драконорождённый", (32, 34), "planned"),
    EntityRef("gnome", "Гном", (35, 37), "planned"),
    EntityRef("half_elf", "Полуэльф", (38, 39), "planned"),
    EntityRef(
        "half_orc",
        "Полуорк",
        (40, 41),
        "partial",
        "database/races/races.yaml#half_orc",
    ),
    EntityRef("tiefling", "Тифлинг", (42, 44), "planned"),
)

CLASSES: tuple[EntityRef, ...] = (
    EntityRef("barbarian", "Варвар", (46, 50), "planned"),
    EntityRef(
        "bard",
        "Бард",
        (51, 55),
        "partial",
        "database/classes/classes.yaml#bard",
    ),
    EntityRef(
        "cleric",
        "Жрец",
        (56, 63),
        "partial",
        "database/classes/classes.yaml#cleric",
    ),
    EntityRef("druid", "Друид", (64, 69), "planned"),
    EntityRef(
        "fighter",
        "Воин",
        (70, 75),
        "partial",
        "database/classes/classes.yaml#fighter",
    ),
    EntityRef("monk", "Монах", (76, 81), "planned"),
    EntityRef("paladin", "Паладин", (82, 88), "planned"),
    EntityRef("ranger", "Следопыт", (89, 93), "planned"),
    EntityRef(
        "rogue",
        "Плут",
        (94, 98),
        "partial",
        "database/classes/classes.yaml#rogue",
    ),
    EntityRef("sorcerer", "Чародей", (99, 104), "planned"),
    EntityRef("warlock", "Колдун", (105, 111), "planned"),
    EntityRef("wizard", "Волшебник", (112, 120), "planned"),
)

BACKGROUNDS: tuple[EntityRef, ...] = (
    EntityRef(
        "acolyte",
        "Прислужник",
        (125, 127),
        "partial",
        "database/backgrounds/backgrounds.yaml#acolyte",
    ),
    EntityRef(
        "charlatan",
        "Шарлатан",
        (127, 128),
        "partial",
        "database/backgrounds/backgrounds.yaml#charlatan",
    ),
    EntityRef(
        "criminal",
        "Преступник",
        (128, 129),
        "partial",
        "database/backgrounds/backgrounds.yaml#criminal",
    ),
    EntityRef(
        "entertainer",
        "Артист",
        (129, 130),
        "partial",
        "database/backgrounds/backgrounds.yaml#entertainer",
    ),
    EntityRef(
        "folk_hero",
        "Народный герой",
        (130, 131),
        "partial",
        "database/backgrounds/backgrounds.yaml#folk_hero",
    ),
    EntityRef(
        "guild_artisan",
        "Гильдейский ремесленник",
        (131, 132),
        "partial",
        "database/backgrounds/backgrounds.yaml#guild_artisan",
    ),
    EntityRef(
        "hermit",
        "Отшельник",
        (132, 133),
        "partial",
        "database/backgrounds/backgrounds.yaml#hermit",
    ),
    EntityRef(
        "noble",
        "Благородный",
        (133, 134),
        "partial",
        "database/backgrounds/backgrounds.yaml#noble",
    ),
    EntityRef(
        "outlander",
        "Чужеземец",
        (134, 135),
        "partial",
        "database/backgrounds/backgrounds.yaml#outlander",
    ),
    EntityRef(
        "sage",
        "Мудрец",
        (135, 136),
        "partial",
        "database/backgrounds/backgrounds.yaml#sage",
    ),
    EntityRef(
        "sailor",
        "Моряк",
        (136, 137),
        "partial",
        "database/backgrounds/backgrounds.yaml#sailor",
    ),
    EntityRef(
        "soldier",
        "Солдат",
        (137, 138),
        "partial",
        "database/backgrounds/backgrounds.yaml#soldier",
    ),
    EntityRef(
        "urchin",
        "Беспризорник",
        (138, 142),
        "partial",
        "database/backgrounds/backgrounds.yaml#urchin",
    ),
)

CHAPTER_PRESERVE: frozenset[str] = frozenset(
    {
        "05-equipment-reference.md",
        "03-subclasses.md",
        "06-feats.md",
        "06-multiclass.md",
        "01-character-creation.md",
    }
)

CHAPTERS: tuple[dict[str, object], ...] = (
    {
        "id": "00-introduction",
        "ru": "Введение",
        "chapter": 0,
        "part": 0,
        "pages": (5, 9),
        "file": "00-introduction.md",
        "mud_status": "partial",
    },
    {
        "id": "01-character-creation",
        "ru": "Создание персонажа",
        "chapter": 1,
        "part": 1,
        "pages": (11, 16),
        "file": "01-character-creation.md",
        "mud_status": "implemented",
    },
    {
        "id": "02-races",
        "ru": "Расы",
        "chapter": 2,
        "part": 1,
        "pages": (17, 44),
        "file": "02-races.md",
        "mud_status": "partial",
    },
    {
        "id": "03-classes",
        "ru": "Классы",
        "chapter": 3,
        "part": 1,
        "pages": (45, 120),
        "file": "03-classes.md",
        "mud_status": "partial",
    },
    {
        "id": "03-subclasses",
        "ru": "Подклассы",
        "chapter": 3,
        "part": 1,
        "pages": (48, 119),
        "file": "03-subclasses.md",
        "mud_status": "planned",
    },
    {
        "id": "04-backgrounds",
        "ru": "Личность и предыстория",
        "chapter": 4,
        "part": 1,
        "pages": (121, 142),
        "file": "04-backgrounds.md",
        "mud_status": "partial",
    },
    {
        "id": "05-equipment",
        "ru": "Снаряжение",
        "chapter": 5,
        "part": 1,
        "pages": (143, 161),
        "file": "05-equipment.md",
        "mud_status": "partial",
    },
    {
        "id": "05-equipment-reference",
        "ru": "Справочник снаряжения",
        "chapter": 5,
        "part": 1,
        "pages": (143, 161),
        "file": "05-equipment-reference.md",
        "mud_status": "partial",
    },
    {
        "id": "06-individual-options",
        "ru": "Индивидуальные опции",
        "chapter": 6,
        "part": 1,
        "pages": (163, 170),
        "file": "06-individual-options.md",
        "mud_status": "partial",
    },
    {
        "id": "06-multiclass",
        "ru": "Мультиклассирование",
        "chapter": 6,
        "part": 1,
        "pages": (163, 165),
        "file": "06-multiclass.md",
        "mud_status": "forbidden",
    },
    {
        "id": "06-feats",
        "ru": "Черты",
        "chapter": 6,
        "part": 1,
        "pages": (165, 170),
        "file": "06-feats.md",
        "mud_status": "partial",
    },
    {
        "id": "07-ability-scores",
        "ru": "Использование характеристик",
        "chapter": 7,
        "part": 2,
        "pages": (173, 180),
        "file": "07-ability-scores.md",
        "mud_status": "partial",
    },
    {
        "id": "08-adventures",
        "ru": "Приключения",
        "chapter": 8,
        "part": 2,
        "pages": (181, 188),
        "file": "08-adventures.md",
        "mud_status": "planned",
    },
    {
        "id": "09-combat",
        "ru": "Сражение",
        "chapter": 9,
        "part": 2,
        "pages": (189, 198),
        "file": "09-combat.md",
        "mud_status": "planned",
    },
    {
        "id": "10-spellcasting",
        "ru": "Использование заклинаний",
        "chapter": 10,
        "part": 3,
        "pages": (201, 206),
        "file": "10-spellcasting.md",
        "mud_status": "planned",
    },
    {
        "id": "11-spells",
        "ru": "Заклинания",
        "chapter": 11,
        "part": 3,
        "pages": (207, 289),
        "file": "11-spells.md",
        "mud_status": "planned",
    },
    {
        "id": "appendices",
        "ru": "Приложения",
        "chapter": 0,
        "part": 0,
        "pages": (290, 326),
        "file": "appendices.md",
        "mud_status": "planned",
    },
)

APPENDICES: tuple[EntityRef, ...] = (
    EntityRef("A-conditions", "Состояния", (290, 293), "planned"),
    EntityRef("B-gods", "Боги мультивселенной", (293, 300), "n/a"),
    EntityRef("C-planes", "Планы существования", (300, 304), "n/a"),
    EntityRef("D-creatures", "Параметры существ", (304, 312), "planned"),
    EntityRef("E-literature", "Литература для вдохновения", (312, 313), "n/a"),
)

SCHOOL_RU_TO_EN: dict[str, str] = {
    "воплощение": "evocation",
    "ограждение": "abjuration",
    "очарование": "enchantment",
    "иллюзия": "illusion",
    "некромантия": "necromancy",
    "преобразование": "transmutation",
    "прорицание": "divination",
    "вызов": "conjuration",
}

RACE_HEADINGS: dict[str, str] = {
    "dwarf": "ДВАРФ",
    "elf": "ЭЛЬФ",
    "halfling": "ПОЛУРОСЛИК",
    "human": "ЧЕЛОВЕК",
    "dragonborn": "ДРАКОНОРОЖД",
    "gnome": "ГНОМ",
    "half_elf": "ПОЛУЭЛЬФ",
    "half_orc": "ПОЛУОРК",
    "tiefling": "ТИФЛИНГ",
}

CLASS_HEADINGS: dict[str, str] = {
    "barbarian": "ВАРВАР",
    "bard": "БАРД",
    "cleric": "ЖРЕЦ",
    "druid": "ДРУИД",
    "fighter": "ВОИН",
    "monk": "МОНАХ",
    "paladin": "ПАЛАДИН",
    "ranger": "СЛЕДОПЫТ",
    "rogue": "ПЛУТ",
    "sorcerer": "ЧАРОДЕЙ",
    "warlock": "КОЛДУН",
    "wizard": "ВОЛШЕБНИК",
}

SPELL_RU_TO_EN: dict[str, str] = {
    "АУРА ЖИВУЧЕСТИ": "aura_of_vitality",
    "АУРА ЖИЗНИ": "aura_of_life",
    "АУРА ОЧИЩЕНИЯ": "aura_of_purity",
    "БЕССЛЕДНОЕ ПЕРЕДВИЖЕНИЕ": "pass_without_trace",
    "БЛАГОСЛОВЕНИЕ": "bless",
    "ВОЛШЕБНАЯ РУКА": "mage_hand",
    "ВОЛШЕБНАЯ СТРЕЛА": "magic_missile",
    "ВОЛШЕБНЫЕ УСТА": "major_image",
    "ГЕРОИЗМ": "heroism",
    "ГАЗООБРАЗНАЯ ФОРМА": "gaseous_form",
    "ГРОМОВОЙ УДАР": "thunderwave",
    "ДРУЖБА": "friends",
    "ЗАЩИТА ОТ ОРУЖИЯ": "blade_ward",
    "ЗЛАЯ НАСМЕШКА": "vicious_mockery",
    "ЛЕЧЕНИЕ РАН": "cure_wounds",
    "ЛЕЧАЩЕЕ СЛОВО": "healing_word",
    "МАЛАЯ ИЛЛЮЗИЯ": "minor_illusion",
    "МЕТКИЙ УДАР": "true_strike",
    "ОГОНЬ ФЕЙ": "faerie_fire",
    "ОГНЕННЫЕ ЛАДОНИ": "burning_hands",
    "ОЧАРОВАНИЕ ЛИЧНОСТИ": "charm_person",
    "ПАДЕНИЕ ПЁРЫШКОМ": "feather_fall",
    "ПОЧИНКА": "mending",
    "СВЕТ": "light",
    "СООБЩЕНИЕ": "message",
    "УСЫПЛЕНИЕ": "sleep",
    "ЩИТ": "shield",
    "ЩИТ ВЕРЫ": "shield_of_faith",
    "ОБНАРУЖЕНИЕ МАГИИ": "detect_magic",
    "РАССЕИВАНИЕ МАГИИ": "dispel_magic",
    "ОГНЕННЫЙ ШАР": "fireball",
    "МОЛНИЕВАЯ СТРЕЛА": "lightning_bolt",
    "НЕВИДИМОСТЬ": "invisibility",
    "ПОЛЁТ": "fly",
    "ТЕЛЕПОРТАЦИЯ": "teleport",
    "ВОСКРЕШЕНИЕ": "resurrection",
    "МЕТЕОРИТНЫЙ ДОЖДЬ": "meteor_swarm",
    "ЖЕЛАНИЕ": "wish",
}
