"""Бонусы HP за уровень из особенностей (раса, черта)."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class HpBonusSource:
    """Именованный бонус HP за уровень (особенность расы или черта)."""

    name: str
    amount: int


def hit_point_bonus_amount(
    mechanics: dict[str, Any], feat: dict[str, Any]
) -> int:
    """Значение hit_point_bonus из feature, если per_level."""
    mtype = feat.get("type") or mechanics.get("type")
    if mtype != "hit_point_bonus" or not mechanics.get("per_level"):
        return 0
    return int(mechanics.get("value", mechanics.get("amount", 0)))


def hit_point_bonus_sources_from_features(
    features: list[dict[str, Any]],
) -> list[HpBonusSource]:
    """Бонусы HP за уровень из features (имя — поле name особенности)."""
    sources: list[HpBonusSource] = []
    for feat in features:
        mechanics = feat.get("mechanics", {})
        if not isinstance(mechanics, dict):
            mechanics = {}
        amount = hit_point_bonus_amount(mechanics, feat)
        if amount <= 0:
            continue
        name = str(feat.get("name", "")).strip() or "?"
        sources.append(HpBonusSource(name=name, amount=amount))
    return sources
