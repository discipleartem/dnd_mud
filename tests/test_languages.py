"""Тесты загрузки языков и пулов выбора."""

import pytest

from core.languages import (
    get_fixed_racial_languages,
    get_racial_language_choices,
    load_languages,
    resolve_language_pool,
)

pytestmark = pytest.mark.usefixtures("catalog_caches_cleared")


def test_load_languages_and_elf_fixed() -> None:
    langs = load_languages("ru")
    ids = {entry["id"] for entry in langs}
    assert "common" in ids
    assert "elvish" in ids
    assert "abyssal" in ids
    assert get_fixed_racial_languages("elf", None) == ["common", "elvish"]


def test_variant_human_and_language_pools() -> None:
    fixed = get_fixed_racial_languages("human", "variant_human")
    assert fixed == ["common"]
    choices = get_racial_language_choices("human", "variant_human")
    assert len(choices) == 1
    assert choices[0][1] == "subrace"
    common_pool = resolve_language_pool("common", [])
    exotic_pool = resolve_language_pool("exotic", [])
    assert "dwarvish" in common_pool
    assert "abyssal" not in common_pool
    assert "abyssal" in exotic_pool
