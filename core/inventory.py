"""Инвентарь персонажа, экипировка и расчёт КД."""

import re
from typing import Any, Literal

from core.classes import character_has_spellcasting
from core.dice import ability_modifier
from core.equipment import (
    armor_category,
    get_armor_name,
    get_equipment_item_name,
    get_tool_name,
    get_weapon_name,
    load_armor,
    load_equipment_item,
    load_weapon,
)
from core.models import Character
from core.proficiency_checks import (
    has_armor_proficiency,
    has_weapon_proficiency,
)

ItemKind = Literal["weapon", "armor", "tool", "equipment"]


def normalize_inventory_item(raw: dict[str, Any]) -> dict[str, Any] | None:
    """Нормализовать запись инвентаря."""
    kind = raw.get("kind")
    item_id = raw.get("id")
    if kind not in ("weapon", "armor", "tool", "equipment"):
        return None
    if not isinstance(item_id, str) or not item_id:
        return None
    qty_raw = raw.get("qty", 1)
    qty = int(qty_raw) if isinstance(qty_raw, int) else 1
    if qty < 1:
        qty = 1
    return {"kind": kind, "id": item_id, "qty": qty}


def expand_pack_contents(item_id: str) -> list[dict[str, Any]]:
    """Развернуть набор (pack) в список предметов."""
    info = load_equipment_item(item_id)
    if info.get("category") != "pack":
        return []
    contents = info.get("contents", [])
    if not isinstance(contents, list):
        return []
    result: list[dict[str, Any]] = []
    for entry in contents:
        if not isinstance(entry, dict):
            continue
        normalized = normalize_inventory_item(entry)
        if normalized:
            result.append(normalized)
    return result


def merge_inventory_items(
    items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Сложить одинаковые предметы по kind+id."""
    merged: dict[tuple[str, str], int] = {}
    order: list[tuple[str, str]] = []
    for raw in items:
        item = normalize_inventory_item(raw) if "kind" in raw else None
        if item is None:
            continue
        key = (str(item["kind"]), str(item["id"]))
        if key not in merged:
            order.append(key)
            merged[key] = 0
        merged[key] += int(item["qty"])
    return [
        {"kind": kind, "id": item_id, "qty": merged[(kind, item_id)]}
        for kind, item_id in order
    ]


def add_items_to_inventory(
    inventory: list[dict[str, Any]],
    new_items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Добавить предметы в инвентарь с развёрткой наборов."""
    expanded: list[dict[str, Any]] = list(inventory)
    for raw in new_items:
        item = normalize_inventory_item(raw)
        if item is None:
            continue
        if (
            item["kind"] == "equipment"
            and load_equipment_item(item["id"]).get("category") == "pack"
        ):
            expanded.extend(expand_pack_contents(item["id"]))
        else:
            expanded.append(item)
    return merge_inventory_items(expanded)


def default_equipped() -> dict[str, Any]:
    """Пустая экипировка."""
    return {
        "armor": None,
        "shield": False,
        "main_hand": None,
        "off_hand": None,
    }


def _armor_ac_value(armor_id: str, dex_mod: int) -> int:
    """Базовый КД от доспеха по PHB."""
    info = load_armor(armor_id)
    base = int(info.get("armor_class", 10))
    bonus_type = str(info.get("modifier_bonus", ""))
    max_dex = info.get("max_dex_modifier")
    dex_part = 0
    if bonus_type == "DEX":
        if isinstance(max_dex, int):
            dex_part = min(dex_mod, max_dex)
        else:
            dex_part = dex_mod
    return base + dex_part


def compute_ac(character: Character) -> int:
    """Класс доспеха персонажа (PHB, без особых умений)."""
    stats = character.stats
    dex_mod = ability_modifier(int(stats.get("dexterity", 10)))
    equipped = character.equipped or default_equipped()
    armor_id = equipped.get("armor")
    ac = 10 + dex_mod
    if isinstance(armor_id, str) and armor_id:
        ac = _armor_ac_value(armor_id, dex_mod)
    if equipped.get("shield"):
        ac += 2
    return ac


def _armor_sort_key(armor_id: str) -> tuple[int, int]:
    """Ключ сортировки: тяжелее и выше базовый КД — лучше."""
    info = load_armor(armor_id)
    cat = armor_category(armor_id)
    cat_rank = {"heavy": 3, "medium": 2, "light": 1}.get(cat, 0)
    return (cat_rank, int(info.get("armor_class", 0)))


def _parse_dice_average(dice: str) -> float:
    """Средний урон по нотации кости (например ``1d8`` → 4.5)."""
    match = re.fullmatch(r"(\d+)d(\d+)", dice.strip())
    if not match:
        return 0.0
    count, sides = int(match.group(1)), int(match.group(2))
    return count * (sides + 1) / 2


def _weapon_properties(weapon_id: str) -> dict[str, Any]:
    props = load_weapon(weapon_id).get("properties")
    return dict(props) if isinstance(props, dict) else {}


def _weapon_is_two_handed(weapon_id: str) -> bool:
    return bool(_weapon_properties(weapon_id).get("two_handed"))


def _weapon_is_light(weapon_id: str) -> bool:
    return bool(_weapon_properties(weapon_id).get("light"))


def _weapon_base_damage_dice(weapon_id: str) -> str:
    damage = load_weapon(weapon_id).get("damage", {})
    if isinstance(damage, dict):
        return str(damage.get("dice", "1d4"))
    return "1d4"


def _weapon_one_handed_damage(weapon_id: str) -> float:
    """Средний урон одной рукой (без versatile в двухручном режиме)."""
    if _weapon_is_two_handed(weapon_id):
        return 0.0
    return _parse_dice_average(_weapon_base_damage_dice(weapon_id))


def _weapon_auto_equip_damage(weapon_id: str) -> tuple[float, bool]:
    """Урон для авто-экипировки: versatile всегда одной рукой."""
    if _weapon_is_two_handed(weapon_id):
        return _parse_dice_average(_weapon_base_damage_dice(weapon_id)), True
    return _weapon_one_handed_damage(weapon_id), False


def _pick_main_weapon(weapons: list[str]) -> tuple[str | None, bool]:
    """Основное оружие с наибольшим уроном (с учётом владения)."""
    if not weapons:
        return None, False
    best_id = weapons[0]
    best_damage = -1.0
    best_two_handed = False
    for weapon_id in weapons:
        damage, two_handed = _weapon_auto_equip_damage(weapon_id)
        if damage > best_damage:
            best_damage = damage
            best_id = weapon_id
            best_two_handed = two_handed
    return best_id, best_two_handed


def _inventory_weapon_ids(character: Character) -> list[str]:
    """Уникальные id оружия в инвентаре."""
    seen: set[str] = set()
    result: list[str] = []
    for item in character.inventory:
        if item.get("kind") != "weapon":
            continue
        weapon_id = str(item.get("id", ""))
        if not weapon_id or weapon_id in seen:
            continue
        seen.add(weapon_id)
        result.append(weapon_id)
    return result


def _proficient_inventory_weapons(character: Character) -> list[str]:
    """Оружие из инвентаря, которым владеет персонаж."""
    profs = character.weapon_proficiencies
    return [
        weapon_id
        for weapon_id in _inventory_weapon_ids(character)
        if has_weapon_proficiency(profs, weapon_id)
    ]


def _pick_off_hand_weapon(weapons: list[str], main_hand: str) -> str | None:
    """Лёгкое одноручное оружие для второй руки (кроме основного)."""
    candidates: list[tuple[float, str]] = []
    for weapon_id in weapons:
        if weapon_id == main_hand:
            continue
        if _weapon_is_two_handed(weapon_id) or not _weapon_is_light(weapon_id):
            continue
        candidates.append((_weapon_one_handed_damage(weapon_id), weapon_id))
    if not candidates:
        return None
    return max(candidates)[1]


def equip_defaults(character: Character) -> dict[str, Any]:
    """Авто-экипировка: лучший доспех, щит и оружие из инвентаря."""
    equipped = default_equipped()
    armor_profs = character.armor_proficiencies

    armor_ids = [
        str(item["id"])
        for item in character.inventory
        if item.get("kind") == "armor"
        and armor_category(str(item["id"])) in ("light", "medium", "heavy")
        and has_armor_proficiency(armor_profs, str(item["id"]))
    ]
    if armor_ids:
        equipped["armor"] = max(armor_ids, key=_armor_sort_key)

    has_shield_item = any(
        item.get("kind") == "armor" and item.get("id") == "shield"
        for item in character.inventory
    )
    shield_proficient = has_armor_proficiency(armor_profs, "shield")
    can_use_shield = has_shield_item and shield_proficient

    weapons = _proficient_inventory_weapons(character)
    main_hand, main_two_handed = _pick_main_weapon(weapons)
    if main_hand:
        equipped["main_hand"] = main_hand

    if main_hand and main_two_handed:
        equipped["shield"] = False
        return equipped

    if can_use_shield:
        equipped["shield"] = True
        return equipped

    if character_has_spellcasting(
        character.class_id, character.subclass_id, character.level
    ):
        return equipped

    off_hand = _pick_off_hand_weapon(weapons, main_hand or "")
    if off_hand:
        equipped["off_hand"] = off_hand
    return equipped


def item_display_name(
    kind: str,
    item_id: str,
    language: str = "ru",
) -> str:
    """Локализованное имя предмета инвентаря."""
    if kind == "weapon":
        return get_weapon_name(item_id, language)
    if kind == "armor":
        return get_armor_name(item_id, language)
    if kind == "tool":
        return get_tool_name(item_id, language)
    return get_equipment_item_name(item_id, language)


def _equipped_item_counts(
    equipped: dict[str, Any],
) -> dict[tuple[str, str], int]:
    """Сколько предметов каждого kind+id занято экипировкой."""
    counts: dict[tuple[str, str], int] = {}
    armor_id = equipped.get("armor")
    if isinstance(armor_id, str) and armor_id:
        key = ("armor", armor_id)
        counts[key] = counts.get(key, 0) + 1
    if equipped.get("shield"):
        key = ("armor", "shield")
        counts[key] = counts.get(key, 0) + 1
    main_hand = equipped.get("main_hand")
    if isinstance(main_hand, str) and main_hand:
        key = ("weapon", main_hand)
        counts[key] = counts.get(key, 0) + 1
    off_hand = equipped.get("off_hand")
    if isinstance(off_hand, str) and off_hand:
        key = ("weapon", off_hand)
        counts[key] = counts.get(key, 0) + 1
    return counts


def inventory_excluding_equipped(
    inventory: list[dict[str, Any]],
    equipped: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """Инвентарь для UI: без экипированного; save не меняется."""
    if not equipped:
        return list(inventory)
    hidden = _equipped_item_counts(equipped)
    if not hidden:
        return list(inventory)
    visible: list[dict[str, Any]] = []
    for item in inventory:
        kind = str(item.get("kind", ""))
        item_id = str(item.get("id", ""))
        qty = int(item.get("qty", 1))
        remaining = qty - hidden.get((kind, item_id), 0)
        if remaining > 0:
            visible.append({"kind": kind, "id": item_id, "qty": remaining})
    return visible


def format_inventory_line(
    inventory: list[dict[str, Any]],
    language: str = "ru",
    *,
    equipped: dict[str, Any] | None = None,
) -> str:
    """Сжатый список инвентаря для UI (без экипированных предметов)."""
    display_items = inventory_excluding_equipped(inventory, equipped)
    parts: list[str] = []
    for item in display_items:
        kind = str(item.get("kind", ""))
        item_id = str(item.get("id", ""))
        qty = int(item.get("qty", 1))
        name = item_display_name(kind, item_id, language)
        if qty > 1:
            parts.append(f"{name} ×{qty}")
        else:
            parts.append(name)
    return ", ".join(parts)


def get_equipped_display(
    character: Character,
    language: str = "ru",
) -> dict[str, str]:
    """Локализованные подписи экипированных предметов."""
    equipped = character.equipped or default_equipped()
    result: dict[str, str] = {}
    armor_id = equipped.get("armor")
    if isinstance(armor_id, str) and armor_id:
        result["armor"] = item_display_name("armor", armor_id, language)
    if equipped.get("shield"):
        result["shield"] = get_armor_name("shield", language)
    main_hand = equipped.get("main_hand")
    if isinstance(main_hand, str) and main_hand:
        result["main_hand"] = item_display_name("weapon", main_hand, language)
    off_hand = equipped.get("off_hand")
    if isinstance(off_hand, str) and off_hand:
        result["off_hand"] = item_display_name("weapon", off_hand, language)
    return result
