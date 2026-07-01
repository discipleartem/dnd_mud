"""Тесты загрузки языков и пулов выбора."""

import re
from typing import Any

import pytest

from core.languages import (
    get_fixed_racial_languages,
    get_racial_language_choices,
    load_languages,
    resolve_language_pool,
)
from ui.menus.languages import select_creation_languages

pytestmark = pytest.mark.usefixtures("catalog_caches_cleared")

_PROMPT_RE = re.compile(
    r"(Язык расы|Язык предыстории) \(\d+/\d+\):|"
    r"(Racial language|Background language) \(\d+/\d+\):"
)


def _pick_prompts_from_calls(calls: list[tuple[object, ...]]) -> list[str]:
    """Первый аргумент get_int_input — текст промпта выбора языка."""
    prompts: list[str] = []
    for call in calls:
        prompt = str(call[0])
        if _PROMPT_RE.search(prompt):
            prompts.append(prompt)
    return prompts


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


def test_language_pick_prompts_acolyte_variant_human(
    monkeypatch: pytest.MonkeyPatch, ru_strings: dict[str, Any]
) -> None:
    """Прислужник: два промпта выбора языка предыстории (1/2 и 2/2)."""
    calls: list[tuple[object, ...]] = []

    def fake_get_int_input(
        prompt: str, *args: object, **kwargs: object
    ) -> int:
        calls.append((prompt, args, kwargs))
        return 1

    monkeypatch.setattr("ui.menus._deps.get_int_input", fake_get_int_input)
    result = select_creation_languages(
        ru_strings, "human", "variant_human", "acolyte", "ru"
    )
    assert result is not None
    prompts = _pick_prompts_from_calls(calls)
    assert any("расы (1/1)" in p for p in prompts)
    assert any("предыстории (1/2)" in p for p in prompts)
    assert any("предыстории (2/2)" in p for p in prompts)
