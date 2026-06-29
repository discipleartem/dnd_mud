"""Тесты загрузки снаряжения."""

from core.equipment import (
    load_armor,
    load_tool,
    load_weapon,
    proficiency_token_label,
    resolve_tool_pool,
    tools_by_category,
    weapon_matches_category,
)
from core.localization import load_strings


def test_load_weapon_has_category():
    """Оружие загружается с категорией."""
    info = load_weapon("longsword")
    assert info.get("category") == "martial_melee"


def test_weapon_matches_simple_category():
    """Простое оружие распознаётся по категории simple."""
    assert weapon_matches_category("simple", "club")
    assert not weapon_matches_category("martial", "club")


def test_tools_by_category_musical():
    """Музыкальные инструменты в категории."""
    pool = tools_by_category("musical_instruments")
    assert "lute" in pool or len(pool) > 0


def test_resolve_tool_pool_land_vehicles():
    """Пул land_vehicles содержит land_vehicles."""
    pool = resolve_tool_pool("land_vehicles")
    assert "land_vehicles" in pool


def test_load_armor_shield():
    """Щит загружается."""
    info = load_armor("shield")
    assert info.get("category") == "shield"


def test_load_tool_thieves():
    """Воровские инструменты."""
    info = load_tool("thieves_tools")
    assert info.get("name")


def test_proficiency_token_label_longbow_ru():
    """Токен longbow локализуется через proficiency.*."""
    strings = load_strings("ru")
    assert proficiency_token_label("longbow", strings, "ru") == "длинные луки"


def test_proficiency_token_label_tool_fallback_en():
    """Инструмент локализуется через tools.*."""
    strings = load_strings("en")
    label = proficiency_token_label("smith_tools", strings, "en")
    assert label == "Smith's tools"
