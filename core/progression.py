"""Прогрессия персонажа: опыт, уровни, HP, ASI, экспертиза, подклассы."""

from collections.abc import Callable
from dataclasses import dataclass, field, replace
from typing import Any

from core.classes import (
    get_class_dict,
    get_class_hit_dice,
    get_subclass_choice_level,
    get_subclass_dict,
    grants_at_level,
    iter_class_grants,
    load_class_full,
)
from core.constants import MAX_CHARACTER_LEVEL, clamp_level
from core.dice import ability_modifier, roll
from core.models import Character
from core.skills import THIEVES_TOOLS_ID, subclass_skills_active
from core.stats import (
    ABILITY_SCORE_DEFAULT,
    ABILITY_SCORE_MAX,
    STAT_NAMES,
    apply_bonuses_to_stats,
)
from core.types import GameDifficulty, StatMap

# ============================================================================
# Константы и пороги опыта
# ============================================================================

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

EASY_START_LEVEL = 3
ASI_FEATURE_ID = "ability_score_improvement"


# ============================================================================
# Опыт и уровни
# ============================================================================


def level_from_xp(experience: int) -> int:
    """Уровень персонажа по накопленному опыту (1–MAX_CHARACTER_LEVEL)."""
    level = 1
    for idx, threshold in enumerate(XP_THRESHOLDS, start=1):
        if experience >= threshold:
            level = idx
    return min(level, MAX_CHARACTER_LEVEL)


def xp_for_level(level: int) -> int:
    """Минимальный накопленный опыт PHB для достижения уровня.

    Используется при создании персонажа. В игре опыт только растёт
    (`grant_experience`); после левелапа избыток над порогом сохраняется.
    """
    level = clamp_level(level)
    return XP_THRESHOLDS[level - 1]


def xp_covers_level(experience: int, level: int) -> bool:
    """Достаточно ли опыта для текущего уровня (>= минимального порога)."""
    return experience >= xp_for_level(level)


def grant_experience(character: Character, amount: int) -> Character:
    """Добавить опыт без повышения уровня (накопительно, без обрезки)."""
    if amount <= 0:
        return character
    return replace(character, experience=character.experience + amount)


def has_pending_level_up(character: Character) -> bool:
    """Есть ли неприменённое повышение уровня по текущему XP."""
    if character.level >= MAX_CHARACTER_LEVEL:
        return False
    return character.level < level_from_xp(character.experience)


# ============================================================================
# Бонусы HP
# ============================================================================


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


# ============================================================================
# Прирост HP
# ============================================================================


def extra_hp_bonus_sources(
    race_id: str | None = None,
    subrace_id: str | None = None,
    feat_ids: list[str] | None = None,
) -> tuple[HpBonusSource, ...]:
    """Именованные бонусы HP за уровень: раса/подраса и черты."""
    from core.feats import get_feat_hp_bonus_sources
    from core.races import get_racial_hp_bonus_sources

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
    constitution = stats.get("constitution", ABILITY_SCORE_DEFAULT)
    con_mod = ability_modifier(constitution)
    hp_bonus = extra_hp_per_level(race_id, subrace_id, feat_ids)
    total = 0
    for lvl in range(1, level + 1):
        total += hp_gain_for_level(
            lvl, hit_dice, con_mod, difficulty, hp_bonus
        )
    return total


# ============================================================================
# ASI (увеличение характеристик)
# ============================================================================


def feat_id_from_asi_choice(asi_value: str) -> str | None:
    """ID черты из сохранённого выбора ASI (``feat:<id>``) или None."""
    if not asi_value.startswith("feat:"):
        return None
    feat_id = asi_value.split(":", 1)[1]
    if not feat_id:
        return None
    return feat_id


def class_grants_asi_at_level(class_id: str, level: int) -> bool:
    """Есть ли у класса умение ASI на указанном уровне."""
    class_info = get_class_dict(class_id)
    if not class_info:
        return False
    for feat in iter_class_grants(class_info):
        if feat.get("id") != ASI_FEATURE_ID:
            continue
        if feat.get("level") == level:
            return True
    return False


def pending_asi_at_level(character: Character, new_level: int) -> bool:
    """На этом уровне ожидается выбор ASI или черты."""
    if not class_grants_asi_at_level(character.class_id, new_level):
        return False
    return str(new_level) not in character.asi_choices


def apply_asi_two_one(stats: StatMap, stat: str) -> StatMap:
    """+2 к одной характеристике (макс. 20)."""
    if stat not in STAT_NAMES:
        return stats.copy()
    bonuses: StatMap = {stat: 2}
    return apply_bonuses_to_stats(stats, bonuses)


def apply_asi_one_two(stats: StatMap, stat_a: str, stat_b: str) -> StatMap:
    """+1 к двум разным характеристикам (макс. 20)."""
    if stat_a not in STAT_NAMES or stat_b not in STAT_NAMES:
        return stats.copy()
    if stat_a == stat_b:
        return stats.copy()
    return apply_bonuses_to_stats(stats, {stat_a: 1, stat_b: 1})


def cap_stats(stats: StatMap) -> StatMap:
    """Ограничить характеристики максимумом 20."""
    result = stats.copy()
    for stat in STAT_NAMES:
        if stat in result and result[stat] > ABILITY_SCORE_MAX:
            result[stat] = ABILITY_SCORE_MAX
    return result


def con_hp_bonus_from_asi(
    old_stats: StatMap, new_stats: StatMap, level: int
) -> int:
    """При росте модификатора CON — +1 max HP за каждый достигнутый уровень."""
    old_con = old_stats.get("constitution", ABILITY_SCORE_DEFAULT)
    new_con = new_stats.get("constitution", ABILITY_SCORE_DEFAULT)
    old_mod = ability_modifier(old_con)
    new_mod = ability_modifier(new_con)
    if new_mod <= old_mod:
        return 0
    return level * (new_mod - old_mod)


def auto_asi_bonus(class_id: str) -> StatMap:
    """Авто-ASI для тестов: +2 к ключевой характеристике класса."""
    class_info = get_class_dict(class_id)
    prime = "strength"
    if isinstance(class_info, dict):
        raw = class_info.get("prime_ability", "strength")
        if isinstance(raw, str) and raw in STAT_NAMES:
            prime = raw
    return {prime: 2}


# ============================================================================
# Экспертиза (компетентность)
# ============================================================================


@dataclass
class ExpertiseAlternative:
    """Альтернативный вариант экспертизы (плут: навык + инструмент)."""

    pick: int
    pool: str
    options: list[str] = field(default_factory=list)


@dataclass
class ExpertiseGrant:
    """Один grant компетентности на уровне класса."""

    feature_id: str
    feature_name: str
    level: int
    pick: int
    pool: str
    alternatives: list[ExpertiseAlternative] = field(default_factory=list)


def _parse_alternatives(
    raw: Any,
) -> list[ExpertiseAlternative]:
    """Разобрать alternatives из YAML."""
    if not isinstance(raw, list):
        return []
    result: list[ExpertiseAlternative] = []
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        pick = int(entry.get("pick", 0))
        pool = str(entry.get("pool", ""))
        options_raw = entry.get("options", [])
        options: list[str] = []
        if isinstance(options_raw, list):
            options = [str(o) for o in options_raw]
        if pick > 0 and pool:
            result.append(
                ExpertiseAlternative(pick=pick, pool=pool, options=options)
            )
    return result


def _grants_from_feature(feat: dict[str, Any]) -> list[ExpertiseGrant]:
    """Извлечь grants из одного class feature."""
    mechanics = feat.get("expertise_mechanics", {})
    if not isinstance(mechanics, dict):
        return []
    raw_grants = mechanics.get("grants", [])
    if not isinstance(raw_grants, list):
        return []

    feature_id = str(feat.get("id", ""))
    feature_name = str(feat.get("name", feature_id))
    result: list[ExpertiseGrant] = []
    for grant in raw_grants:
        if not isinstance(grant, dict):
            continue
        level = int(grant.get("level", 0))
        pick = int(grant.get("pick", 0))
        pool = str(grant.get("pool", ""))
        if level < 1 or pick < 1 or not pool:
            continue
        result.append(
            ExpertiseGrant(
                feature_id=feature_id,
                feature_name=feature_name,
                level=level,
                pick=pick,
                pool=pool,
                alternatives=_parse_alternatives(grant.get("alternatives")),
            )
        )
    return result


def get_expertise_grants(
    class_id: str, character_level: int
) -> list[ExpertiseGrant]:
    """Grants компетентности, доступные на текущем уровне при создании."""
    class_info = load_class_full(class_id)
    features = class_info.get("features", [])
    if not isinstance(features, list):
        return []

    grants: list[ExpertiseGrant] = []
    for feat in features:
        if not isinstance(feat, dict):
            continue
        for grant in _grants_from_feature(feat):
            if grant.level <= character_level:
                grants.append(grant)
    grants.sort(key=lambda g: g.level)
    return grants


def expertise_step_required(class_id: str, character_level: int) -> bool:
    """Нужен ли экран выбора экспертизы при создании."""
    return bool(get_expertise_grants(class_id, character_level))


def _prior_expertise_picks(
    class_id: str, character_level: int, before_level: int
) -> int:
    """Сумма pick по grants с level < before_level (без альтернатив)."""
    return sum(
        g.pick
        for g in get_expertise_grants(class_id, character_level)
        if not g.alternatives and g.level < before_level
    )


def grant_expertise_satisfied(
    character: Character, grant: ExpertiseGrant
) -> bool:
    """Компетентность по grant уже выбрана на персонаже."""
    if grant.alternatives:
        return bool(character.skill_expertise or character.tool_expertise)
    prior = _prior_expertise_picks(
        character.class_id, character.level, grant.level
    )
    return len(character.skill_expertise) >= prior + grant.pick


def pending_expertise_grants(character: Character) -> list[ExpertiseGrant]:
    """Grants компетентности, ещё не выбранные на текущем уровне."""
    grants = get_expertise_grants(character.class_id, character.level)
    return [g for g in grants if not grant_expertise_satisfied(character, g)]


def validate_expertise_selection(
    grant: ExpertiseGrant,
    proficiencies: list[str],
    selected_skills: list[str],
    selected_tools: list[str],
    *,
    used_alternative: bool = False,
) -> bool:
    """Проверить корректность выбора компетентности."""
    if used_alternative:
        if not grant.alternatives:
            return False
        skill_alt = next(
            (a for a in grant.alternatives if a.pool == "proficient_skills"),
            None,
        )
        tool_alt = next(
            (a for a in grant.alternatives if a.pool == "tools"), None
        )
        if skill_alt is None or tool_alt is None:
            return False
        if len(selected_skills) != skill_alt.pick:
            return False
        if len(selected_tools) != tool_alt.pick:
            return False
        prof_set = set(proficiencies)
        return all(s in prof_set for s in selected_skills) and all(
            t in tool_alt.options for t in selected_tools
        )

    if len(selected_skills) != grant.pick:
        return False
    if selected_tools:
        return False
    if len(set(selected_skills)) != grant.pick:
        return False
    prof_set = set(proficiencies)
    return all(s in prof_set for s in selected_skills)


def default_rogue_tool_expertise() -> list[str]:
    """ID воровских инструментов для альтернативы плута."""
    return [THIEVES_TOOLS_ID]


# ============================================================================
# Подклассы
# ============================================================================


def features_up_to_level(
    features: list[Any], max_level: int = MAX_CHARACTER_LEVEL
) -> list[dict[str, Any]]:
    """Отфильтровать умения с level <= max_level."""
    result: list[dict[str, Any]] = []
    for feat in features:
        if not isinstance(feat, dict):
            continue
        level = feat.get("level")
        if isinstance(level, int) and level > max_level:
            continue
        result.append(feat)
    return result


def start_level_for_difficulty(difficulty: GameDifficulty) -> int:
    """Стартовый уровень персонажа при создании."""
    if difficulty == "easy":
        return EASY_START_LEVEL
    return 1


def subclass_offered_at_creation(
    difficulty: GameDifficulty,
    class_id: str,
    start_level: int | None = None,
) -> bool:
    """Нужен ли экран выбора подкласса при создании персонажа."""
    if start_level is None:
        start_level = start_level_for_difficulty(difficulty)
    choice_level = get_subclass_choice_level(class_id)

    match difficulty:
        case "easy":
            return start_level >= choice_level
        case "normal":
            return True
        case "hardcore":
            return choice_level <= start_level


def subclass_is_active(character: Character) -> bool:
    """Подкласс механически активен на текущем уровне."""
    if character.subclass_id is None:
        return False
    return character.level >= get_subclass_choice_level(character.class_id)


def needs_subclass_npc(character: Character) -> bool:
    """HardCore-персонажу нужен NPC-наставник для выбора подкласса."""
    if character.difficulty != "hardcore":
        return False
    if character.subclass_id is not None:
        return False
    choice_level = get_subclass_choice_level(character.class_id)
    if choice_level <= 1:
        return False
    return character.level >= choice_level


# ============================================================================
# Особенности класса
# ============================================================================


def class_features_applied_at_creation(
    class_id: str, subclass_id: str | None, start_level: int
) -> bool:
    """Особенности подкласса выбраны при создании (старт >= ур. архетипа)."""
    return subclass_skills_active(class_id, subclass_id, start_level)


def needs_class_feature_picks(character: Character) -> bool:
    """Нужен выбор особенностей класса/подкласса (наставник, сценарий)."""
    if not subclass_is_active(character):
        return False
    return not character.class_features_applied


def subclass_skill_picks_pending(character: Character) -> bool:
    """Ещё не выбраны навыки подкласса."""
    from core.skills import get_subclass_skill_choices

    if not character.subclass_id:
        return False
    return bool(
        get_subclass_skill_choices(
            character.class_id,
            character.subclass_id,
            character.level,
        )
    )


def mark_class_features_applied(character: Character) -> Character:
    """Пометить особенности класса/подкласса как применённые."""
    return replace(character, class_features_applied=True)


# ============================================================================
# Повышение уровня
# ============================================================================


def apply_level_up(character: Character, hp_gain: int) -> Character:
    """Повысить персонажа на один уровень с заданным приростом HP.

    Поле ``experience`` не меняется — избыток над порогом уровня сохраняется.
    """
    if not has_pending_level_up(character):
        return character
    new_level = character.level + 1
    updated = replace(
        character,
        level=new_level,
        max_hp=character.max_hp + hp_gain,
        current_hp=character.current_hp + hp_gain,
    )
    return apply_progression_grants_at_level(updated, new_level)


def _apply_progression_grant(
    character: Character, grant: dict[str, Any]
) -> Character:
    """Применить один grant progression без UI-подвыборов."""
    if grant.get("choice"):
        return character
    from core.grants import proficiency_tokens_and_skills_from_grant
    from core.proficiencies import merge_proficiency_tokens
    from core.skills import merge_proficiencies

    weapons, armors, tools, skills = proficiency_tokens_and_skills_from_grant(
        grant
    )
    updated = replace(
        character,
        weapon_proficiencies=merge_proficiency_tokens(
            character.weapon_proficiencies, weapons
        ),
        armor_proficiencies=merge_proficiency_tokens(
            character.armor_proficiencies, armors
        ),
        tool_proficiencies=merge_proficiency_tokens(
            character.tool_proficiencies, tools
        ),
        skills=merge_proficiencies(character.skills, skills),
    )
    if grant.get("type") == "save_proficiency":
        ability = grant.get("ability")
        if isinstance(ability, str):
            updated = replace(
                updated,
                save_proficiencies=merge_proficiencies(
                    updated.save_proficiencies, [ability]
                ),
            )
    return updated


def apply_progression_grants_at_level(
    character: Character, level: int
) -> Character:
    """Авто-применение grants класса/подкласса на уровне."""
    char = character
    class_info = get_class_dict(char.class_id)
    for grant in grants_at_level(class_info, level):
        char = _apply_progression_grant(char, grant)
    if char.subclass_id:
        subclass_info = get_subclass_dict(char.class_id, char.subclass_id)
        if subclass_info:
            for grant in grants_at_level(subclass_info, level):
                char = _apply_progression_grant(char, grant)
    return char


@dataclass
class AsiResolution:
    """Результат выбора ASI/черты на уровне."""

    character: Character
    con_bonus: int = 0
    tough_bonus: int = 0


def _headless_asi_resolution(
    character: Character, new_level: int
) -> AsiResolution:
    """Авто-ASI или сохранённый выбор (без UI)."""
    from core.feats import (
        apply_feat_grants_to_character,
        resolve_feat_ability_bonuses,
        tough_hp_adjustment_on_acquire,
    )
    from core.stats import apply_bonuses_to_stats

    char = character
    old_stats = char.stats.copy()
    con_bonus = 0
    tough_bonus = 0
    asi_key = str(new_level)
    had_tough = "tough" in char.feat_ids
    asi_value = ""

    if pending_asi_at_level(char, new_level):
        prime = next(iter(auto_asi_bonus(char.class_id)))
        stats = cap_stats(apply_asi_two_one(char.stats, prime))
        con_bonus = con_hp_bonus_from_asi(old_stats, stats, new_level)
        asi_choices = dict(char.asi_choices)
        asi_value = "asi"
        asi_choices[asi_key] = asi_value
        char = replace(char, stats=stats, asi_choices=asi_choices)
    elif asi_key in char.asi_choices:
        asi_value = char.asi_choices[asi_key]
        stats = old_stats.copy()
        feat_ids = list(char.feat_ids)
        feat_choices = dict(char.feat_choices)
        feat_id = feat_id_from_asi_choice(asi_value)
        sub: dict[str, Any] = {}
        if feat_id and feat_id not in feat_ids:
            sub = feat_choices.get(feat_id, {})
            feat_ids.append(feat_id)
            bonuses = resolve_feat_ability_bonuses(feat_id, sub)
            stats = cap_stats(apply_bonuses_to_stats(stats, bonuses))
        con_bonus = con_hp_bonus_from_asi(old_stats, stats, new_level)
        char = replace(
            char,
            stats=stats,
            feat_ids=feat_ids,
            feat_choices=feat_choices,
        )
        if feat_id:
            char = apply_feat_grants_to_character(char, feat_id, sub)

    if feat_id_from_asi_choice(asi_value) == "tough" and not had_tough:
        tough_bonus = tough_hp_adjustment_on_acquire(new_level)

    return AsiResolution(
        character=char, con_bonus=con_bonus, tough_bonus=tough_bonus
    )


def process_pending_level_ups(
    character: Character,
    *,
    resolve_asi: (
        Callable[[Character, int], AsiResolution | None] | None
    ) = None,
    on_level_up: (
        Callable[[Character, int, HpGainBreakdown, int, int], bool] | None
    ) = None,
) -> Character:
    """Применить все ожидающие повышения; resolve_asi — UI или headless."""
    char = character
    while has_pending_level_up(char):
        new_level = char.level + 1
        con_bonus = 0
        tough_bonus = 0

        if pending_asi_at_level(char, new_level):
            resolution: AsiResolution | None
            if resolve_asi is None:
                resolution = _headless_asi_resolution(char, new_level)
            else:
                resolution = resolve_asi(char, new_level)
            if resolution is None:
                break
            char = resolution.character
            con_bonus = resolution.con_bonus
            tough_bonus = resolution.tough_bonus
        elif str(new_level) in char.asi_choices:
            resolution = _headless_asi_resolution(char, new_level)
            char = resolution.character
            con_bonus = resolution.con_bonus
            tough_bonus = resolution.tough_bonus

        roll_feat_ids = list(char.feat_ids)
        if tough_bonus > 0:
            roll_feat_ids = [
                feat_id for feat_id in roll_feat_ids if feat_id != "tough"
            ]

        breakdown = hp_gain_breakdown_for_level_up(
            char.class_id,
            char.stats,
            new_level,
            char.difficulty,
            char.race,
            char.subrace,
            roll_feat_ids,
        )
        if on_level_up is not None and not on_level_up(
            char, new_level, breakdown, con_bonus, tough_bonus
        ):
            break
        char = apply_level_up(char, breakdown.total + con_bonus + tough_bonus)
    return char


def resolve_pending_level_ups(character: Character) -> Character:
    """Применить все ожидающие повышения без UI."""
    return process_pending_level_ups(character)


def apply_experience(character: Character, amount: int) -> Character:
    """Добавить опыт и сразу применить все повышения уровня (без UI)."""
    return resolve_pending_level_ups(grant_experience(character, amount))


__all__ = [
    # XP thresholds
    "XP_THRESHOLDS",
    # XP and levels
    "level_from_xp",
    "xp_for_level",
    "xp_covers_level",
    "grant_experience",
    "has_pending_level_up",
    # HP bonuses
    "HpBonusSource",
    "hit_point_bonus_amount",
    "hit_point_bonus_sources_from_grants",
    # HP gain
    "extra_hp_bonus_sources",
    "extra_hp_per_level",
    "HpGainBreakdown",
    "hp_gain_for_level",
    "hp_gain_breakdown_for_level_up",
    "roll_hp_gain_for_level_up",
    "max_hp_for_level",
    # ASI
    "ASI_FEATURE_ID",
    "feat_id_from_asi_choice",
    "class_grants_asi_at_level",
    "pending_asi_at_level",
    "apply_asi_two_one",
    "apply_asi_one_two",
    "cap_stats",
    "con_hp_bonus_from_asi",
    "auto_asi_bonus",
    # Expertise
    "ExpertiseAlternative",
    "ExpertiseGrant",
    "get_expertise_grants",
    "expertise_step_required",
    "grant_expertise_satisfied",
    "pending_expertise_grants",
    "validate_expertise_selection",
    "default_rogue_tool_expertise",
    # Subclasses
    "EASY_START_LEVEL",
    "features_up_to_level",
    "start_level_for_difficulty",
    "subclass_offered_at_creation",
    "subclass_is_active",
    "needs_subclass_npc",
    # Class features
    "class_features_applied_at_creation",
    "needs_class_feature_picks",
    "subclass_skill_picks_pending",
    "mark_class_features_applied",
    # Level up
    "apply_level_up",
    "apply_progression_grants_at_level",
    "AsiResolution",
    "process_pending_level_ups",
    "resolve_pending_level_ups",
    "apply_experience",
    # Re-exported
    "roll",
]
