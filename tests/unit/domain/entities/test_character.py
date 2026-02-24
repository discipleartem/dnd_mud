"""Тесты для доменной сущности персонажа."""

import pytest

from src.domain.entities.character import Character
from src.domain.entities.race import Race, SubRace
from src.domain.value_objects.ability_scores import AbilityScores
from src.domain.value_objects.size import Size, SizeCategory


class TestCharacter:
    """Тесты для сущности персонажа."""
    
    def test_character_creation_valid_data(self):
        """Тест создания персонажа с валидными данными."""
        ability_scores = AbilityScores(
            strength=16, dexterity=14, constitution=15,
            intelligence=12, wisdom=13, charisma=10
        )
        
        character = Character(
            name="Тестовый персонаж",
            level=5,
            ability_scores=ability_scores
        )
        
        assert character.name == "Тестовый персонаж"
        assert character.level == 5
        assert character.ability_scores == ability_scores
        assert character.size.category == SizeCategory.MEDIUM
    
    def test_character_creation_empty_name(self):
        """Тест создания персонажа с пустым именем."""
        with pytest.raises(ValueError, match="Имя персонажа не может быть пустым"):
            Character(name="")
    
    def test_character_creation_short_name(self):
        """Тест создания персонажа с коротким именем."""
        with pytest.raises(ValueError, match="Имя персонажа должно содержать минимум 2 символа"):
            Character(name="А")
    
    def test_character_creation_long_name(self):
        """Тест создания персонажа с длинным именем."""
        long_name = "А" * 51
        with pytest.raises(ValueError, match="Имя персонажа не может превышать 50 символов"):
            Character(name=long_name)
    
    def test_character_creation_invalid_level(self):
        """Тест создания персонажа с невалидным уровнем."""
        with pytest.raises(ValueError, match="Уровень персонажа должен быть в диапазоне 1-20"):
            Character(name="Тест", level=0)
        
        with pytest.raises(ValueError, match="Уровень персонажа должен быть в диапазоне 1-20"):
            Character(name="Тест", level=21)
    
    def test_character_level_up(self):
        """Тест повышения уровня персонажа."""
        character = Character(name="Тест", level=1)
        
        character.level_up()
        assert character.level == 2
        
        # Проверяем повышение до максимального уровня
        for _ in range(2, 20):
            character.level_up()
        assert character.level == 20
        
        # Попытка повышения выше максимального
        with pytest.raises(ValueError, match="Персонаж уже на максимальном уровне"):
            character.level_up()
    
    def test_character_languages(self):
        """Тест управления языками персонажа."""
        character = Character(name="Тест")
        
        # Изначально нет языков
        assert character.languages == []
        
        # Изучение нового языка
        result = character.learn_language("elven")
        assert result is True
        assert "elven" in character.languages
        assert character.knows_language("elven")
        
        # Попытка изучить тот же язык
        with pytest.raises(ValueError, match="Персонаж уже знает язык"):
            character.learn_language("elven")
        
        # Забывание языка
        result = character.forget_language("elven")
        assert result is True
        assert "elven" not in character.languages
        assert not character.knows_language("elven")
        
        # Попытка забыть неизученный язык
        result = character.forget_language("dwarven")
        assert result is False
    
    def test_character_ability_modifiers(self):
        """Тест модификаторов характеристик."""
        ability_scores = AbilityScores(
            strength=16,  # +3
            dexterity=14,  # +2
            constitution=8,  # -1
            intelligence=12,  # +1
            wisdom=10,  # +0
            charisma=7    # -2
        )
        
        character = Character(
            name="Тест",
            ability_scores=ability_scores
        )
        
        modifiers = character.get_all_ability_modifiers()
        assert modifiers["strength"] == 3
        assert modifiers["dexterity"] == 2
        assert modifiers["constitution"] == -1
        assert modifiers["intelligence"] == 1
        assert modifiers["wisdom"] == 0
        assert modifiers["charisma"] == -2
    
    def test_character_change_race(self):
        """Тест изменения расы персонажа."""
        ability_scores = AbilityScores(10, 10, 10, 10, 10, 10)
        
        character = Character(
            name="Тест",
            ability_scores=ability_scores
        )
        
        # Изначально нет расы
        assert character.race is None
        assert character.size.category == SizeCategory.MEDIUM
        
        # Создаем тестовую расу
        race = Race(
            name="Эльф",
            size=Size.from_category(SizeCategory.MEDIUM),
            speed=30,
            ability_bonuses={"dexterity": 2, "constitution": -2}
        )
        
        character.change_race(race)
        
        assert character.race == race
        assert character.size.category == SizeCategory.MEDIUM
        
        # Проверяем применение бонусов
        assert character.ability_scores.dexterity == 12  # 10 + 2
        assert character.ability_scores.constitution == 8   # 10 - 2
    
    def test_character_validation(self):
        """Тест валидации персонажа."""
        # Валидный персонаж
        ability_scores = AbilityScores(10, 10, 10, 10, 10, 10)
        character = Character(
            name="Тест",
            level=5,
            ability_scores=ability_scores
        )
        
        errors = character.validate()
        assert len(errors) == 0
        
        # Невалидный персонаж
        invalid_character = Character(
            name="",  # Пустое имя
            level=25,  # Невалидный уровень
            ability_scores=ability_scores
        )
        
        errors = invalid_character.validate()
        assert len(errors) >= 2
        assert any("имя" in error.lower() for error in errors)
        assert any("уровень" in error.lower() for error in errors)
    
    def test_character_summary(self):
        """Тест получения сводной информации."""
        ability_scores = AbilityScores(16, 14, 15, 12, 13, 10)
        race = Race(
            name="Человек",
            size=Size.from_category(SizeCategory.MEDIUM),
            speed=30,
            ability_bonuses={}
        )
        
        character = Character(
            name="Тестовый персонаж",
            race=race,
            character_class="Воин",
            level=3,
            ability_scores=ability_scores
        )
        
        summary = character.get_summary()
        
        assert summary["name"] == "Тестовый персонаж"
        assert summary["race"] == "Человек"
        assert summary["character_class"] == "Воин"
        assert summary["level"] == 3
        assert summary["size"] == "medium"
        assert summary["speed"] == 30
        assert summary["ability_scores"] is not None
        assert summary["ability_modifiers"] is not None
    
    def test_character_string_representation(self):
        """Тест строкового представления персонажа."""
        character = Character(
            name="Тест",
            character_class="Воин",
            level=5
        )
        
        str_repr = str(character)
        assert "Тест" in str_repr
        assert "Воин" in str_repr
        assert "5 уровня" in str_repr
        
        # Без класса
        character_no_class = Character(name="Тест")
        str_repr_no_class = str(character_no_class)
        assert "Тест" in str_repr_no_class
        assert "Без расы" in str_repr_no_class
