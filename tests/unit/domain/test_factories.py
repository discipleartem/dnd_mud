"""Тесты для фабрик доменных сущностей."""


from src.domain.factories.character_factory import CharacterFactory
from src.domain.factories.race_factory import RaceFactory
from src.domain.value_objects.size import SizeCategory


class TestCharacterFactory:
    """Тесты фабрики персонажей."""

    def test_create_character_default(self) -> None:
        """Тест создания персонажа с параметрами по умолчанию."""
        character = CharacterFactory.create_character("Тестовый персонаж")

        assert character.name == "Тестовый персонаж"
        assert character.race is None
        assert character.character_class == ""
        assert character.level == 1
        # Проверяем что языки пустые через приватный атрибут
        assert len(character._known_languages) == 0

    def test_create_character_with_params(self) -> None:
        """Тест создания персонажа с параметрами."""
        race = RaceFactory.create_human()
        character = CharacterFactory.create_character(
            name="Герой",
            race=race,
            character_class="Воин",
            level=5,
            languages=["Общий"],
        )

        assert character.name == "Герой"
        assert character.race == race
        assert character.character_class == "Воин"
        assert character.level == 5
        assert "Общий" in character._known_languages

    def test_create_with_race(self) -> None:
        """Тест создания персонажа с расой."""
        race = RaceFactory.create_human()
        character = CharacterFactory.create_with_race(
            name="Человек-воин",
            race=race,
            character_class="Воин",
        )

        assert character.name == "Человек-воин"
        assert character.race == race
        assert character.character_class == "Воин"
        assert character.level == 1


class TestRaceFactory:
    """Тесты фабрики рас."""

    def test_create_race_default(self) -> None:
        """Тест создания расы с параметрами по умолчанию."""
        race = RaceFactory.create_race("Тестовая раса", "Описание")

        assert race.name == "Тестовая раса"
        assert race.description == "Описание"
        assert race.size.category == SizeCategory.MEDIUM
        assert race.ability_bonuses == {}
        assert race.speed == 30
        assert race.languages == []
        assert race.features == []

    def test_create_race_with_params(self) -> None:
        """Тест создания расы с параметрами."""
        from src.domain.entities.race import Feature

        race = RaceFactory.create_race(
            name="Эльф",
            description="Изящная раса",
            size_category=SizeCategory.MEDIUM,
            ability_bonuses={"dexterity": 2},
            speed=30,
            languages=["Эльфийский", "Общий"],
            features=[Feature("Обучение эльфов", "Профессия с оружием")],
        )

        assert race.name == "Эльф"
        assert race.description == "Изящная раса"
        assert race.ability_bonuses == {"dexterity": 2}
        assert race.speed == 30
        assert "Эльфийский" in race.languages
        assert "Общий" in race.languages
        assert len(race.features) == 1
        assert race.features[0].name == "Обучение эльфов"

    def test_create_human(self) -> None:
        """Тест создания стандартной расы людей."""
        human = RaceFactory.create_human()

        assert human.name == "Человек"
        assert human.ability_bonuses == {
            "strength": 1, "dexterity": 1, "constitution": 1,
            "intelligence": 1, "wisdom": 1, "charisma": 1
        }
        assert human.speed == 30
        assert "Общий" in human.languages

    def test_create_elf(self) -> None:
        """Тест создания стандартной расы эльфов."""
        elf = RaceFactory.create_elf()

        assert elf.name == "Эльф"
        assert elf.ability_bonuses == {"dexterity": 2}
        assert elf.speed == 30
        assert "Эльфийский" in elf.languages
        assert "Общий" in elf.languages

    def test_create_dwarf(self) -> None:
        """Тест создания стандартной расы дварфов."""
        dwarf = RaceFactory.create_dwarf()

        assert dwarf.name == "Дварф"
        assert dwarf.ability_bonuses == {"constitution": 2}
        assert dwarf.speed == 25
        assert "Дварфийский" in dwarf.languages
        assert "Общий" in dwarf.languages

    def test_create_subrace(self) -> None:
        """Тест создания подрасы."""
        from src.domain.entities.race import Feature

        subrace = RaceFactory.create_subrace(
            name="Высший эльф",
            description="Просвещенные эльфы",
            ability_bonuses={"intelligence": 1},
            inherit_base_abilities=True,
            languages=["Высший эльфийский"],
            features=[Feature("Дополнительная заклинанность", "Можно выучить дополнительное заклинание")],
        )

        assert subrace.name == "Высший эльф"
        assert subrace.ability_bonuses == {"intelligence": 1}
        assert subrace.inherit_base_abilities is True
        assert "Высший эльфийский" in subrace.languages
        assert len(subrace.features) == 1
