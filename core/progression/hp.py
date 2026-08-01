"""Расчёт HP при создании и повышении уровня."""

from dataclasses import dataclass

from core.catalogs.classes import get_class_hit_dice
from core.constants import ability_modifier, clamp_level
from core.mechanics.dice import roll
from core.mechanics.hp_bonus import (
    HpBonusSource,
    get_racial_hp_bonus_sources,
)
from core.mechanics.stats import ABILITY_SCORE_DEFAULT
from core.types import GameDifficulty, StatMap


def extra_hp_bonus_sources(
    race_id: str | None = None,
    subrace_id: str | None = None,
    feat_ids: list[str] | None = None,
) -> tuple[HpBonusSource, ...]:
    """Именованные бонусы HP за уровень: раса/подраса и черты."""
    from core.feats.apply import get_feat_hp_bonus_sources

    sources: list[HpBonusSource] = []
    if race_id:
        sources.extend(get_racial_hp_bonus_sources(race_id, subrace_id))
    sources.extend(get_feat_hp_bonus_sources(feat_ids or []))
    return tuple(sources)


def extra_hp_per_level(
    race_id: str | None = None,
    subrace_id: str | None = None,
    feat_ids: list[str] | None = None,
) -> int:
    """Суммарный бонус HP за уровень: раса/подраса + черты."""
    sources = extra_hp_bonus_sources(race_id, subrace_id, feat_ids)
    return sum(s.amount for s in sources)


@dataclass(frozen=True)
class HpGainBreakdown:
    """Прирост HP: кость (или среднее/бросок), CON и внешние бонусы."""

    die_part: int
    con_mod: int
    bonus_sources: tuple[HpBonusSource, ...] = ()
    is_first_level: bool = False
    dice_roll: int | None = None

    @property
    def extra_bonus(self) -> int:
        """Сумма расовых и чертовых бонусов за уровень."""
        return sum(source.amount for source in self.bonus_sources)

    @property
    def class_part(self) -> int:
        """Часть от кости хитов и модификатора Телосложения."""
        if self.is_first_level or self.dice_roll is not None:
            return max(1, self.die_part + self.con_mod)
        return self.die_part + self.con_mod

    @property
    def total(self) -> int:
        """Полный прирост max HP за уровень."""
        return self.class_part + self.extra_bonus


def hp_gain_for_level(
    level: int,
    hit_dice: int,
    con_mod: int,
    difficulty: GameDifficulty = "normal",
    racial_hp_bonus: int = 0,
) -> int:
    """Прирост максимальных HP за один уровень класса."""
    if difficulty == "hardcore":
        return max(1, roll(1, hit_dice) + con_mod) + racial_hp_bonus
    if level <= 1:
        return max(1, hit_dice + con_mod) + racial_hp_bonus
    return hit_dice // 2 + 1 + con_mod + racial_hp_bonus


def hp_gain_breakdown_for_level_up(
    class_id: str,
    stats: StatMap,
    new_level: int,
    difficulty: GameDifficulty,
    race_id: str | None = None,
    subrace_id: str | None = None,
    feat_ids: list[str] | None = None,
) -> HpGainBreakdown:
    """Разбивка прироста HP за повышение до new_level."""
    hit_dice = get_class_hit_dice(class_id)
    constitution = stats.get("constitution", ABILITY_SCORE_DEFAULT)
    con_mod = ability_modifier(constitution)
    bonus_sources = extra_hp_bonus_sources(race_id, subrace_id, feat_ids)
    if difficulty == "hardcore":
        dice = roll(1, hit_dice)
        return HpGainBreakdown(
            die_part=dice,
            con_mod=con_mod,
            bonus_sources=bonus_sources,
            dice_roll=dice,
        )
    if new_level <= 1:
        return HpGainBreakdown(
            die_part=hit_dice,
            con_mod=con_mod,
            bonus_sources=bonus_sources,
            is_first_level=True,
        )
    return HpGainBreakdown(
        die_part=hit_dice // 2 + 1,
        con_mod=con_mod,
        bonus_sources=bonus_sources,
    )


def max_hp_for_level(
    class_id: str,
    stats: StatMap,
    level: int,
    difficulty: GameDifficulty = "normal",
    race_id: str | None = None,
    subrace_id: str | None = None,
    feat_ids: list[str] | None = None,
) -> int:
    """Максимум HP на заданном уровне с учётом режима сложности."""
    level = clamp_level(level)
    hit_dice = get_class_hit_dice(class_id)
    constitution = stats.get("constitution", ABILITY_SCORE_DEFAULT)
    con_mod = ability_modifier(constitution)
    hp_bonus = extra_hp_per_level(race_id, subrace_id, feat_ids)
    total = 0
    for lvl in range(1, level + 1):
        total += hp_gain_for_level(
            lvl, hit_dice, con_mod, difficulty, hp_bonus
        )
    return total
