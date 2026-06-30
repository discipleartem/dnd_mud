"""Тесты загрузки языков и пулов выбора."""

import re

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


def test_language_pick_prompts_variant_human_noble(monkeypatch, ru_strings):
    """Промпты: раса (1/1) и предыстория (1/1), без глобального (2/2)."""
    calls: list[tuple[object, ...]] = []

    def fake_get_int_input(
        prompt: str, *args: object, **kwargs: object
    ) -> int:
        calls.append((prompt, args, kwargs))
        values = [1, 1]
        return values[len(calls) - 1]

    monkeypatch.setattr("ui.menus._deps.get_int_input", fake_get_int_input)
    result = select_creation_languages(
        ru_strings, "human", "variant_human", "noble", "ru"
    )
    assert result is not None
    prompts = _pick_prompts_from_calls(calls)
    assert any("расы (1/1)" in p for p in prompts)
    assert any("предыстории (1/1)" in p for p in prompts)
    assert not any("предыстории (2/2)" in p for p in prompts)
    assert not any("Язык (1/2)" in p for p in prompts)


def test_language_pick_prompts_variant_human_acolyte(monkeypatch, ru_strings):
    """Прислужник: раса (1/1), предыстория (1/2)(2/2), без (1/3)."""
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
    assert not any("(1/3)" in p for p in prompts)
    assert not any("(3/3)" in p for p in prompts)


def test_language_pick_prompts_variant_human_charlatan(
    monkeypatch, ru_strings
):
    """Шарлатан без языка предыстории — только расовый промпт."""
    calls: list[tuple[object, ...]] = []

    def fake_get_int_input(
        prompt: str, *args: object, **kwargs: object
    ) -> int:
        calls.append((prompt, args, kwargs))
        return 1

    monkeypatch.setattr("ui.menus._deps.get_int_input", fake_get_int_input)
    result = select_creation_languages(
        ru_strings, "human", "variant_human", "charlatan", "ru"
    )
    assert result is not None
    prompts = _pick_prompts_from_calls(calls)
    assert len(prompts) == 1
    assert "расы (1/1)" in prompts[0]
    assert not any("предыстории" in p for p in prompts)
