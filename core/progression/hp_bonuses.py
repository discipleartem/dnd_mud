"""Бонусы HP за уровень из особенностей (раса, черта)."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class HpBonusSource:
    """Именованный бонус HP за уровень (особенность расы или черта)."""

    name: str
    amount: int


def hit_point_bonus_amount(mechanics: dict[str, Any]) -> int:
    """Значение hit_point_bonus из grant."""
    if mechanics.get("type") != "hit_point_bonus" or not mechanics.get(
        "per_level"
    ):
        return 0
    return int(mechanics.get("amount", 0))


def hit_point_bonus_sources_from_grants(
    grants: list[dict[str, Any]],
) -> list[HpBonusSource]:
    """Бонусы HP за уровень из grants."""
    sources: list[HpBonusSource] = []
    for grant in grants:
        amount = hit_point_bonus_amount(grant)
        if amount <= 0:
            continue
        name = str(grant.get("name", "")).strip() or "?"
        sources.append(HpBonusSource(name=name, amount=amount))
    return sources
