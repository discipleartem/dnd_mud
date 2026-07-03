"""Типы для группировки владений и компетентности персонажа.

Используется для упрощения структуры Character и уменьшения дублирования.
"""

from dataclasses import dataclass, field


@dataclass
class Proficiencies:
    """Владения персонажа: оружием, доспехами, инструментами."""

    weapons: list[str] = field(default_factory=list)
    armor: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)

    def to_lists(self) -> tuple[list[str], list[str], list[str]]:
        """Преобразовать в кортеж списков для совместимости с API."""
        return self.weapons, self.armor, self.tools

    @classmethod
    def from_lists(
        cls,
        weapons: list[str] | None = None,
        armor: list[str] | None = None,
        tools: list[str] | None = None,
    ) -> "Proficiencies":
        """Создать из списков для совместимости с существующим API."""
        return cls(
            weapons=list(weapons) if weapons else [],
            armor=list(armor) if armor else [],
            tools=list(tools) if tools else [],
        )


@dataclass
class Expertise:
    """Компетентность персонажа: навыки и инструменты."""

    skills: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)

    def to_lists(self) -> tuple[list[str], list[str]]:
        """Преобразовать в кортеж списков для совместимости с API."""
        return self.skills, self.tools

    @classmethod
    def from_lists(
        cls,
        skills: list[str] | None = None,
        tools: list[str] | None = None,
    ) -> "Expertise":
        """Создать из списков для совместимости с существующим API."""
        return cls(
            skills=list(skills) if skills else [],
            tools=list(tools) if tools else [],
        )
