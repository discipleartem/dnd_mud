"""Тесты загрузки языков и пулов выбора."""

import re

import pytest

from core.languages import (
    get_fixed_racial_languages,
    get_racial_language_choices,
    load_languages,
    resolve_language_pool,
)
from ui.menus.languages import select_creation_languages

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


@pytest.mark.parametrize(
    "background,expected_checks",
    [
        (
            "noble",
            [
                "расы (1/1)",
                "предыстории (1/1)",
                "not:предыстории (2/2)",
                "not:Язык (1/2)",
            ],
        ),
        (
            "acolyte",
            [
                "расы (1/1)",
                "предыстории (1/2)",
                "предыстории (2/2)",
                "not:(1/3)",
                "not:(3/3)",
            ],
        ),
        (
            "charlatan",
            ["len:1", "расы (1/1)", "not:предыстории"],
        ),
    ],
)
def test_language_pick_prompts_variant_human(
    monkeypatch, ru_strings, background, expected_checks
):
    """Промпты выбора языков для variant human по предыстории."""
    calls: list[tuple[object, ...]] = []

    def fake_get_int_input(
        prompt: str, *args: object, **kwargs: object
    ) -> int:
        calls.append((prompt, args, kwargs))
        return 1

    monkeypatch.setattr("ui.menus._deps.get_int_input", fake_get_int_input)
    result = select_creation_languages(
        ru_strings, "human", "variant_human", background, "ru"
    )
    assert result is not None
    prompts = _pick_prompts_from_calls(calls)
    for check in expected_checks:
        if check.startswith("not:"):
            assert not any(check[4:] in p for p in prompts)
        elif check.startswith("len:"):
            assert len(prompts) == int(check[4:])
        else:
            assert any(check in p for p in prompts)
