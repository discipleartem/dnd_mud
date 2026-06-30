"""Тесты загрузки языков и пулов выбора."""

from core.languages import (
    get_fixed_racial_languages,
    get_racial_language_choices,
    load_languages,
    resolve_language_pool,
)


def test_load_languages_has_common_and_exotic():
    """Каталог содержит обычные и экзотические языки PHB."""
    langs = load_languages("ru")
    ids = {entry["id"] for entry in langs}
    assert "common" in ids
    assert "elvish" in ids
    assert "abyssal" in ids
    assert "draconic" in ids


def test_elf_fixed_languages():
    """Эльф знает общий и эльфийский автоматически."""
    fixed = get_fixed_racial_languages("elf", None)
    assert fixed == ["common", "elvish"]


def test_variant_human_fixed_and_choice_languages():
    """Вариант человека: Общий + один язык на выбор (PHB)."""
    fixed = get_fixed_racial_languages("human", "variant_human")
    assert fixed == ["common"]
    choices = get_racial_language_choices("human", "variant_human")
    assert len(choices) == 1
    mechanics, source = choices[0]
    assert source == "subrace"
    assert mechanics.get("pool") == "common"


def test_high_elf_language_choice_pool_common():
    """High elf: дополнительный язык только из common."""
    choices = get_racial_language_choices("elf", "high_elf")
    assert len(choices) == 1
    mechanics, source = choices[0]
    assert source == "subrace"
    assert mechanics.get("pool", "common") == "common"
    pool = resolve_language_pool(
        mechanics.get("pool", "common"), ["common", "elvish"]
    )
    assert "dwarvish" in pool
    assert "abyssal" not in pool


def test_exotic_pool_only_with_explicit_spec():
    """Exotic доступен только при pool: exotic."""
    common_pool = resolve_language_pool("common", [])
    exotic_pool = resolve_language_pool("exotic", [])
    assert "abyssal" not in common_pool
    assert "abyssal" in exotic_pool
