"""Прогрессия персонажа: опыт и уровни (PHB, макс. 10 уровень)."""

from dataclasses import dataclass, replace

from core.classes import get_class_hit_dice
from core.dice import ability_modifier, roll
from core.feats import HpBonusSource, get_feat_hp_bonus_sources
from core.levels import MAX_CHARACTER_LEVEL, clamp_level
from core.models import Character
from core.races import get_racial_hp_bonus_sources
from core.types import GameDifficulty, StatMap


def extra_hp_bonus_sources(
    race_id: str | None = None,
    subrace_id: str | None = None,
    feat_ids: list[str] | None = None,
) -> tuple[HpBonusSource, ...]:
    """Именованные бонусы HP за уровень: раса/подраса и черты."""
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
        if self.is_first_level:
            return max(1, self.die_part + self.con_mod)
        if self.dice_roll is not None:
            return self.dice_roll + self.con_mod
        return self.die_part + self.con_mod

    @property
    def total(self) -> int:
        """Полный прирост max HP за уровень."""
        return self.class_part + self.extra_bonus


XP_THRESHOLDS: list[int] = [
    0,
    300,
    900,
    2700,
    6500,
    14000,
    23000,
    34000,
    48000,
    64000,
]


def level_from_xp(experience: int) -> int:
    """Уровень персонажа по накопленному опыту (1–MAX_CHARACTER_LEVEL)."""
    level = 1
    for idx, threshold in enumerate(XP_THRESHOLDS, start=1):
        if experience >= threshold:
            level = idx
    return min(level, MAX_CHARACTER_LEVEL)


def hp_gain_for_level(
    level: int,
    hit_dice: int,
    con_mod: int,
    difficulty: GameDifficulty = "normal",
    racial_hp_bonus: int = 0,
) -> int:
    """Прирост максимальных HP за один уровень класса."""
    if difficulty == "hardcore":
        return roll(1, hit_dice) + con_mod + racial_hp_bonus
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
    con_mod = ability_modifier(stats.get("constitution", 10))
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


def roll_hp_gain_for_level_up(
    class_id: str,
    stats: StatMap,
    new_level: int,
    difficulty: GameDifficulty,
    race_id: str | None = None,
    subrace_id: str | None = None,
    feat_ids: list[str] | None = None,
) -> tuple[int, int | None]:
    """Прирост HP за повышение до new_level.

    Для HardCore возвращает также значение броска кости.
    """
    breakdown = hp_gain_breakdown_for_level_up(
        class_id,
        stats,
        new_level,
        difficulty,
        race_id,
        subrace_id,
        feat_ids,
    )
    return breakdown.total, breakdown.dice_roll


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
    con_mod = ability_modifier(stats.get("constitution", 10))
    hp_bonus = extra_hp_per_level(race_id, subrace_id, feat_ids)
    total = 0
    for lvl in range(1, level + 1):
        total += hp_gain_for_level(
            lvl, hit_dice, con_mod, difficulty, hp_bonus
        )
    return total


def grant_experience(character: Character, amount: int) -> Character:
    """Добавить опыт без повышения уровня."""
    if amount <= 0:
        return character
    return replace(character, experience=character.experience + amount)


def has_pending_level_up(character: Character) -> bool:
    """Есть ли неприменённое повышение уровня по текущему XP."""
    if character.level >= MAX_CHARACTER_LEVEL:
        return False
    return character.level < level_from_xp(character.experience)


def apply_level_up(character: Character, hp_gain: int) -> Character:
    """Повысить персонажа на один уровень с заданным приростом HP."""
    if not has_pending_level_up(character):
        return character
    new_level = character.level + 1
    return replace(
        character,
        level=new_level,
        max_hp=character.max_hp + hp_gain,
        current_hp=character.current_hp + hp_gain,
    )


def resolve_pending_level_ups(character: Character) -> Character:
    """Применить все ожидающие повышения без UI.

    Для тестов и apply_experience.
    """
    char = character
    while has_pending_level_up(char):
        new_level = char.level + 1
        gain, _ = roll_hp_gain_for_level_up(
            char.class_name,
            char.stats,
            new_level,
            char.difficulty,
            char.race,
            char.subrace,
            char.feat_ids,
        )
        char = apply_level_up(char, gain)
    return char


def apply_experience(character: Character, amount: int) -> Character:
    """Добавить опыт и сразу применить все повышения уровня (без UI)."""
    return resolve_pending_level_ups(grant_experience(character, amount))
