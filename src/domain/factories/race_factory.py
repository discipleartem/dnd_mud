"""Фабрика для создания рас.

Реализует паттерн Factory для инкапсуляции логики создания рас.
Следует принципам Domain-Driven Design и Clean Architecture.
"""

from src.domain.entities.race import Feature, Race, SubRace
from src.domain.value_objects.size import Size, SizeCategory


class RaceFactory:
    """Фабрика для создания рас D&D.

    Инкапсулирует сложную логику создания рас с правильными
    значениями по умолчанию и валидацией.
    """

    @staticmethod
    def create_race(
        name: str,
        description: str,
        size_category: SizeCategory = SizeCategory.MEDIUM,
        ability_bonuses: dict[str, int] | None = None,
        speed: int = 30,
        languages: list[str] | None = None,
        features: list[Feature] | None = None,
    ) -> Race:
        """Создать расу с параметрами по умолчанию.

        Args:
            name: Название расы
            description: Описание расы
            size_category: Категория размера
            ability_bonuses: Бонусы к характеристикам
            speed: Скорость передвижения
            languages: Список языков расы
            features: Список особенностей расы

        Returns:
            Созданная раса
        """
        # Значения по умолчанию
        if ability_bonuses is None:
            ability_bonuses = {}

        if languages is None:
            languages = []

        if features is None:
            features = []

        # Создание размера
        size = Size.from_category(size_category)

        return Race(
            name=name,
            description=description,
            size=size,
            ability_bonuses=ability_bonuses,
            speed=speed,
            languages=languages,
            features=features,
        )

    @staticmethod
    def create_subrace(
        name: str,
        description: str,
        ability_bonuses: dict[str, int] | None = None,
        inherit_base_abilities: bool = True,
        languages: list[str] | None = None,
        features: list[Feature] | None = None,
    ) -> SubRace:
        """Создать подрасу.

        Args:
            name: Название подрасы
            description: Описание подрасы
            ability_bonuses: Бонусы к характеристикам
            inherit_base_abilities: Наследовать бонусы базовой расы
            languages: Список языков подрасы
            features: Список особенностей подрасы

        Returns:
            Созданная подраса
        """
        # Значения по умолчанию
        if ability_bonuses is None:
            ability_bonuses = {}

        if languages is None:
            languages = []

        if features is None:
            features = []

        return SubRace(
            name=name,
            description=description,
            ability_bonuses=ability_bonuses,
            inherit_base_abilities=inherit_base_abilities,
            languages=languages,
            features=features,
        )

    @staticmethod
    def create_human() -> Race:
        """Создать стандартную расу людей.

        Returns:
            Раса людей с стандартными параметрами
        """
        features = [
            Feature(
                "Универсальность", "Можно увеличить любую характеристику на 1"
            ),
            Feature(
                "Дополнительный язык", "Можно выучить один дополнительный язык"
            ),
        ]

        return RaceFactory.create_race(
            name="Человек",
            description="Универсальная и адаптивная раса",
            size_category=SizeCategory.MEDIUM,
            ability_bonuses={
                "strength": 1,
                "dexterity": 1,
                "constitution": 1,
                "intelligence": 1,
                "wisdom": 1,
                "charisma": 1,
            },
            speed=30,
            languages=["Общий"],
            features=features,
        )

    @staticmethod
    def create_elf() -> Race:
        """Создать стандартную расу эльфов.

        Returns:
            Раса эльфов с стандартными параметрами
        """
        features = [
            Feature(
                "Обучение эльфов",
                "Профессия с длинным мечом, коротким мечом, луком",
            ),
            Feature("Трассировка", "Преимущество при проверках на поиск"),
            Feature("Бессоние", "Не нуждается во сне"),
            Feature("Чувство фей", "Преимущество против очарования"),
        ]

        return RaceFactory.create_race(
            name="Эльф",
            description="Изящная и долгоживущая раса",
            size_category=SizeCategory.MEDIUM,
            ability_bonuses={"dexterity": 2},
            speed=30,
            languages=["Эльфийский", "Общий"],
            features=features,
        )

    @staticmethod
    def create_dwarf() -> Race:
        """Создать стандартную расу дварфов.

        Returns:
            Раса дварфов с стандартными параметрами
        """
        features = [
            Feature("Стойкость дварфов", "Преимущество против яда"),
            Feature(
                "Тренировка дварфов", "Профессия с боевым топором, молотом"
            ),
            Feature(
                "Каменная кожа", "Преимущество против физических повреждений"
            ),
        ]

        return RaceFactory.create_race(
            name="Дварф",
            description="Выносливая и стойкая раса",
            size_category=SizeCategory.MEDIUM,
            ability_bonuses={"constitution": 2},
            speed=25,
            languages=["Дварфийский", "Общий"],
            features=features,
        )
