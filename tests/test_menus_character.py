"""Тесты UI: выбор персонажа, подрасы, new game, приключения."""

import re

import pytest

from core.models import Adventure, Character
from ui.menus import (
    _creation_steps,
    _deps,
    character_flow,
    characters_menu,
    new_game,
)
from ui.menus import settings as settings_menu
from ui.menus._selectors import select_class, select_subclass, select_subrace


def _patch_load_characters(
    monkeypatch: pytest.MonkeyPatch, characters: list[Character]
) -> None:
    monkeypatch.setattr(_deps, "load_characters", lambda: characters)


def _noop_press_enter(monkeypatch: pytest.MonkeyPatch) -> None:
    from ui.menus import _common

    monkeypatch.setattr(_common, "_press_enter", lambda strings: None)


def test_half_orc_auto_selects_single_subrace(
    monkeypatch, capsys, patch_int_input
):
    """Полуорк с одной подрасой выбирается автоматически."""
    strings = {
        "character": {
            "subrace_caption": "ОПИСАНИЕ РАСЫ И ВЫБОР ПОДРАСЫ",
        }
    }
    race = {
        "name": "Полуорк",
        "description": "Полуорки — сильные и выносливые воины",
        "subraces": {
            "half_orc": {
                "name": "Полуорк",
                "description": "Полуорки — сильные и выносливые воины",
                "ability_bonuses": {"strength": 2},
            }
        },
    }

    monkeypatch.setattr(
        _deps, "load_race_full", lambda race_id, language="ru": race
    )

    selected, subrace_id = select_subrace(strings, "half_orc")

    assert selected is True
    assert subrace_id == "half_orc"


def test_human_shows_standard_and_variant_subraces(
    monkeypatch, capsys, patch_int_input
):
    """Человек показывает подрасы standard и variant_human."""
    strings = {
        "character": {
            "subrace_caption": "ОПИСАНИЕ РАСЫ И ВЫБОР ПОДРАСЫ",
            "race_description": "  {desc}",
            "features_label": "  Особенности:",
            "feature_line": "    • {name}: {desc}",
            "subraces_label": "  Подрасы:",
            "subrace_prompt": "Выберите подрасу: ",
            "back": "Назад",
        }
    }
    race = {
        "name": "Человек",
        "description": "Описание человека",
        "subraces": {
            "standard": {
                "name": "Человек (стандарт)",
                "description": "Стандартный человек",
                "ability_bonuses": {"strength": 1},
            },
            "variant_human": {
                "name": "Человек (вариант)",
                "description": "Вариант человека",
                "inherit": {"ability_bonuses": False, "grants": False},
                "grants": [],
            },
        },
    }

    monkeypatch.setattr(
        _deps, "load_race_full", lambda race_id, language="ru": race
    )
    patch_int_input(monkeypatch, [1])

    selected, subrace_id = select_subrace(strings, "human")
    output = capsys.readouterr().out

    assert selected is True
    assert subrace_id == "standard"
    assert "Человек (стандарт)" in output
    assert "Человек (вариант)" in output


def test_create_character_back_from_subrace_exits(
    monkeypatch, ru_strings, patch_int_input
):
    """Назад с подрасы — к расе; повторный назад выходит из flow."""
    monkeypatch.setattr(
        character_flow,
        "select_difficulty",
        lambda strings: "normal",
    )
    monkeypatch.setattr(
        _deps,
        "get_str_input",
        lambda *args, **kwargs: "Hero",
    )
    monkeypatch.setattr(
        _deps,
        "load_races",
        lambda language="ru": [{"id": "human", "name": "Человек"}],
    )
    subrace_calls = {"n": 0}

    def fake_subrace(strings, race_id, language="ru"):
        subrace_calls["n"] += 1
        return False, None

    monkeypatch.setattr(_creation_steps, "select_subrace", fake_subrace)
    patch_int_input(monkeypatch, [1, 0])

    result = character_flow.show_create_character_flow(ru_strings)

    assert result is None
    assert subrace_calls["n"] == 1


def test_hardcore_back_from_stats_keeps_rolls(
    monkeypatch, capsys, ru_strings, patch_int_input
):
    """HardCore: «Назад» с подтверждения сохраняет броски 4d6."""
    from ui.menus.stats import stats_methods

    monkeypatch.setattr(
        character_flow,
        "select_difficulty",
        lambda strings: "hardcore",
    )
    monkeypatch.setattr(
        _deps,
        "get_str_input",
        lambda *args, **kwargs: "Hero",
    )
    monkeypatch.setattr(
        _deps,
        "load_races",
        lambda language="ru": [{"id": "elf", "name": "Эльф"}],
    )
    monkeypatch.setattr(
        _creation_steps,
        "select_subrace",
        lambda strings, race_id, language="ru": (True, "wood_elf"),
    )
    monkeypatch.setattr(
        _creation_steps,
        "select_creation_languages",
        lambda *args, **kwargs: ["common", "elvish"],
    )

    def fake_background(*args, **kwargs):
        return ("folk_hero", ["survival", "animal_handling"])

    monkeypatch.setattr(
        _creation_steps,
        "select_creation_background",
        fake_background,
    )
    monkeypatch.setattr(
        _creation_steps,
        "select_creation_proficiencies",
        lambda *args, **kwargs: (
            ["simple"],
            ["light"],
            ["lute", "flute", "drum"],
        ),
    )
    monkeypatch.setattr(
        _creation_steps,
        "select_class",
        lambda strings, language="ru": {"id": "bard"},
    )
    monkeypatch.setattr(
        _creation_steps,
        "select_creation_skills",
        lambda *args, **kwargs: ["performance", "persuasion", "deception"],
    )
    monkeypatch.setattr(
        _creation_steps,
        "select_creation_expertise",
        lambda *args, **kwargs: ([], []),
    )
    monkeypatch.setattr(
        _creation_steps,
        "_save_created_character",
        lambda state: Character(name="Hero", race="elf", class_id="bard"),
    )
    monkeypatch.setattr(
        _creation_steps,
        "_print_success_and_wait",
        lambda strings, message: None,
    )
    roll_sequence = iter([17, 12, 4, 11, 13, 9, 99, 99, 99, 99, 99, 99])
    roll_calls = {"count": 0}

    def fake_roll() -> int:
        roll_calls["count"] += 1
        return next(roll_sequence)

    monkeypatch.setattr(_deps, "roll_ability_score", fake_roll)
    monkeypatch.setattr(stats_methods, "_press_enter", lambda strings: None)
    patch_int_input(monkeypatch, [1, 0, 1])

    character_flow.show_create_character_flow(ru_strings)
    output = capsys.readouterr().out

    assert roll_calls["count"] == 6
    assert "17" in output
    assert "99" not in output


def test_hardcore_back_to_race_clears_rolls(
    monkeypatch, ru_strings, patch_int_input
):
    """HardCore: возврат к выбору расы сбрасывает сохранённые броски."""
    from ui.menus.stats import stats_methods

    monkeypatch.setattr(
        character_flow,
        "select_difficulty",
        lambda strings: "hardcore",
    )
    monkeypatch.setattr(
        _deps,
        "get_str_input",
        lambda *args, **kwargs: "Hero",
    )
    monkeypatch.setattr(
        _deps,
        "load_races",
        lambda language="ru": [{"id": "elf", "name": "Эльф"}],
    )
    subrace_calls = {"n": 0}

    def fake_subrace(strings, race_id, language="ru"):
        subrace_calls["n"] += 1
        if subrace_calls["n"] == 1:
            return True, "wood_elf"
        if subrace_calls["n"] == 2:
            return False, None
        return True, "wood_elf"

    monkeypatch.setattr(_creation_steps, "select_subrace", fake_subrace)
    monkeypatch.setattr(
        _creation_steps,
        "select_creation_languages",
        lambda *args, **kwargs: ["common", "elvish"],
    )

    def fake_background(*args, **kwargs):
        return ("soldier", ["athletics", "intimidation"])

    monkeypatch.setattr(
        _creation_steps,
        "select_creation_background",
        fake_background,
    )
    monkeypatch.setattr(
        _creation_steps,
        "select_creation_proficiencies",
        lambda *args, **kwargs: (
            ["simple", "martial"],
            ["light", "medium", "heavy", "shield"],
            ["dice_set"],
        ),
    )
    monkeypatch.setattr(
        _creation_steps,
        "select_class",
        lambda strings, language="ru": {"id": "fighter"},
    )
    monkeypatch.setattr(
        _creation_steps,
        "select_creation_skills",
        lambda *args, **kwargs: ["athletics", "intimidation"],
    )
    monkeypatch.setattr(
        _creation_steps,
        "select_creation_expertise",
        lambda *args, **kwargs: ([], []),
    )
    monkeypatch.setattr(
        _creation_steps,
        "_save_created_character",
        lambda state: Character(name="Hero", race="elf", class_id="fighter"),
    )
    monkeypatch.setattr(
        _creation_steps,
        "_print_success_and_wait",
        lambda strings, message: None,
    )
    roll_sequence = iter([10, 10, 10, 10, 10, 10, 11, 11, 11, 11, 11, 11])
    roll_calls = {"count": 0}

    def fake_roll() -> int:
        roll_calls["count"] += 1
        return next(roll_sequence)

    monkeypatch.setattr(_deps, "roll_ability_score", fake_roll)
    monkeypatch.setattr(stats_methods, "_press_enter", lambda strings: None)
    patch_int_input(monkeypatch, [1, 0, 1, 1])

    character_flow.show_create_character_flow(ru_strings)

    assert roll_calls["count"] == 12


def test_select_character_shows_cards_with_difficulty(
    monkeypatch, capsys, ru_strings, patch_int_input
):
    """Список персонажей показывает имя, расу, класс и сложность."""
    normal_char = Character(
        name="Hero Normal",
        race="human",
        class_id="fighter",
        difficulty="normal",
        stats={"strength": 16, "dexterity": 14},
        current_hp=12,
    )
    hardcore_char = Character(
        name="Hero HC",
        race="elf",
        class_id="bard",
        difficulty="hardcore",
        current_hp=9,
    )

    monkeypatch.setattr(
        _deps, "load_characters", lambda: [normal_char, hardcore_char]
    )
    patch_int_input(monkeypatch, [0])

    result = new_game._select_character(
        ru_strings, [normal_char, hardcore_char]
    )
    output = capsys.readouterr().out

    assert result is None
    assert "Hero Normal" in output
    assert "Hero HC" in output
    assert "Человек" in output
    assert "Эльф" in output
    assert output.count("языки:") == 2
    assert output.count("предыстория:") == 2
    assert output.count("навыки:") == 2
    assert output.count("компетентность:") == 2
    assert "Сложность:" in output
    assert "HardCore" in output
    assert "Создать нового персонажа" in output


def test_select_character_shows_subrace_name(
    monkeypatch, capsys, ru_strings, patch_int_input
):
    """Подраса отображается читаемым названием, а не ID."""
    character = Character(
        name="Variant Hero",
        race="human",
        class_id="cleric",
        difficulty="hardcore",
        subrace="variant_human",
        stats=dict.fromkeys(
            [
                "strength",
                "dexterity",
                "constitution",
                "intelligence",
                "wisdom",
                "charisma",
            ],
            10,
        ),
        current_hp=10,
    )

    monkeypatch.setattr(_deps, "load_characters", lambda: [character])
    patch_int_input(monkeypatch, [0])

    new_game._select_character(ru_strings, [character])
    output = capsys.readouterr().out

    assert "подраса:" in output
    assert "вариант" in output
    assert "variant_human" not in output


def test_select_character_create_via_enter(monkeypatch, capsys, ru_strings):
    """Enter без ввода на пункте «Создать» возвращает 'create'."""
    character = Character(
        name="Hero",
        race="human",
        class_id="fighter",
        difficulty="normal",
    )
    monkeypatch.setattr(_deps, "load_characters", lambda: [character])

    from ui.input_handler import get_int_input

    monkeypatch.setattr(_deps, "get_int_input", get_int_input)
    monkeypatch.setattr("builtins.input", lambda prompt: "")
    assert new_game._select_character(ru_strings, [character]) == "create"
    output = capsys.readouterr().out
    assert "[Enter]" in output
    assert "Создать нового персонажа" in output
    assert "2. Создать" not in output


def test_select_adventure_filters_by_character_difficulty(
    monkeypatch, capsys, ru_strings, patch_int_input
):
    """Недоступные приключения показываются отдельным блоком."""
    character = Character(
        name="Normal Hero",
        race="human",
        class_id="fighter",
        difficulty="normal",
    )
    available = Adventure(
        id="tutorial",
        name={"ru": "Обучение"},
        description="desc",
    )
    blocked = Adventure(
        id="hc_only",
        name={"ru": "HardCore Quest"},
        description="desc",
        hardcore_only=True,
    )

    monkeypatch.setattr(_deps, "load_adventures", lambda: [available, blocked])
    patch_int_input(monkeypatch, [0])

    result = new_game._select_adventure(ru_strings, "ru", character)
    output = capsys.readouterr().out

    assert result is None
    assert "Обучение" in output
    assert "HardCore Quest" in output
    assert "Недоступные приключения" in output
    assert "требуется режим HardCore" in output


def test_select_adventure_choice_returns_adventure(
    monkeypatch, ru_strings, patch_int_input
):
    """Выбор доступного приключения возвращает объект Adventure."""
    character = Character(
        name="Normal Hero",
        race="human",
        class_id="fighter",
        difficulty="normal",
    )
    tutorial = Adventure(
        id="tutorial",
        name={"ru": "Обучение"},
        description="desc",
    )

    monkeypatch.setattr(_deps, "load_adventures", lambda: [tutorial])
    patch_int_input(monkeypatch, [1])

    result = new_game._select_adventure(ru_strings, "ru", character)

    assert result is not None
    assert result.id == "tutorial"


def test_new_game_no_characters_goes_to_create(monkeypatch):
    """Без персонажей — сразу создание."""
    calls = {"select": 0, "create": 0}

    def select_character(strings):
        calls["select"] += 1

    def create_flow(strings, language="ru"):
        calls["create"] += 1

    monkeypatch.setattr(_deps, "load_characters", lambda: [])
    monkeypatch.setattr(
        character_flow, "show_create_character_flow", create_flow
    )

    new_game.show_new_game_flow({}, {"language": "ru"})

    assert calls == {"select": 0, "create": 1}


def test_new_game_back_returns_one_step(monkeypatch):
    """Назад из выбора приключения возвращает к выбору персонажа."""
    calls = {"character": 0, "adventure": 0}
    character = Character(
        name="Test Hero",
        race="human",
        class_id="fighter",
    )

    def select_character(strings, characters, language="ru"):
        calls["character"] += 1
        return character if calls["character"] == 1 else None

    def select_adventure(strings, language, char):
        calls["adventure"] += 1
        return None

    monkeypatch.setattr(_deps, "load_characters", lambda: [character])
    monkeypatch.setattr(new_game, "_select_character", select_character)
    monkeypatch.setattr(new_game, "_select_adventure", select_adventure)

    new_game.show_new_game_flow({}, {"language": "ru"})

    assert calls == {"character": 2, "adventure": 1}


def test_languages_menu_order_depends_on_locale(
    monkeypatch, capsys, ru_strings, en_strings, patch_int_input
):
    """Порядок языков в меню зависит от текущей локали."""
    patch_int_input(monkeypatch, [0, 0])

    settings_menu.show_languages_menu(ru_strings, {"language": "ru"})
    ru_output = capsys.readouterr().out
    assert re.search(r"1.*English", ru_output)
    assert re.search(r"2.*Русский", ru_output)

    settings_menu.show_languages_menu(en_strings, {"language": "en"})
    en_output = capsys.readouterr().out
    assert re.search(r"1.*Русский", en_output)
    assert re.search(r"2.*English", en_output)


def test_characters_menu_shows_hub_options(
    monkeypatch, capsys, ru_strings, patch_int_input
):
    """Hub «Персонажи» показывает список и пункты создания/удаления."""
    character = Character(
        name="Hero",
        race="human",
        class_id="fighter",
        save_slug="hero",
    )
    _patch_load_characters(monkeypatch, [character])
    patch_int_input(monkeypatch, [0])

    characters_menu.show_characters_menu(ru_strings)
    output = capsys.readouterr().out

    assert "ПЕРСОНАЖИ" in output
    assert "Hero" in output
    assert "Создать персонажа" in output
    assert "Удалить персонажа" in output
    assert "Удалить всех персонажей" in output


def test_characters_menu_delete_one_confirmed(
    monkeypatch, ru_strings, patch_int_input
):
    """Удаление персонажа вызывает delete_character после подтверждения."""
    character = Character(
        name="Hero",
        race="human",
        class_id="fighter",
        save_slug="hero",
    )
    deleted: list[str] = []

    def fake_delete(slug: str) -> bool:
        deleted.append(slug)
        return True

    _patch_load_characters(monkeypatch, [character])
    monkeypatch.setattr(_deps, "delete_character", fake_delete)
    patch_int_input(monkeypatch, [2, 1, 1, 0])
    _noop_press_enter(monkeypatch)

    characters_menu.show_characters_menu(ru_strings)

    assert deleted == ["hero"]


def test_characters_menu_delete_all_cancelled(
    monkeypatch, capsys, ru_strings, patch_int_input
):
    """Отмена удаления всех персонажей не вызывает delete_all_characters."""
    character = Character(
        name="Hero",
        race="human",
        class_id="fighter",
        save_slug="hero",
    )
    deleted_all_called: list[bool] = []

    def fake_delete_all() -> int:
        deleted_all_called.append(True)
        return 0

    _patch_load_characters(monkeypatch, [character])
    monkeypatch.setattr(_deps, "delete_all_characters", fake_delete_all)
    patch_int_input(monkeypatch, [3, 0, 0])
    _noop_press_enter(monkeypatch)

    characters_menu.show_characters_menu(ru_strings)
    output = capsys.readouterr().out

    assert deleted_all_called == []
    assert "Удаление отменено" in output


def test_select_class_shows_description_and_features(
    monkeypatch, capsys, ru_strings, patch_int_input
):
    """Экран выбора класса показывает описание и умения из YAML."""
    patch_int_input(monkeypatch, [1])

    result = select_class(ru_strings, "ru")
    output = capsys.readouterr().out

    assert result is not None
    assert result.get("id") == "fighter"
    assert "Воин" in output
    assert "Особенности" in output
    assert "Атлетика" in output
    assert "acrobatics" not in output


def test_select_subclass_shows_subclass_features(
    monkeypatch, capsys, ru_strings, patch_int_input
):
    """Экран выбора подкласса показывает архетипы и их умения."""
    patch_int_input(monkeypatch, [1])

    subclass_id = select_subclass(ru_strings, "fighter", "ru")
    output = capsys.readouterr().out

    assert subclass_id == "battle_master"
    assert "Архетипы" in output
    assert "Мастер боевых искусств" in output
    assert "Уровень 3:" in output
    assert "Боевое превосходство" in output


def test_skill_pick_list_grays_proficient_skills(capsys, ru_strings):
    """Занятые навыки отображаются с пометкой «уже владеете»."""
    from core.skills import get_class_skill_config
    from ui.menus.skills import _print_skill_pick_list

    pool, _ = get_class_skill_config("fighter")
    available = _print_skill_pick_list(ru_strings, pool, ["perception"])
    output = capsys.readouterr().out

    assert "уже владеете" in output
    assert "Восприятие" in output
    assert "perception" not in available
    assert "athletics" in available


def test_proficient_summary_shows_racial_source(capsys, ru_strings):
    """Блок «Уже владеете» показывает навык и источник (раса)."""
    from ui.menus.skills import _print_proficient_summary

    _print_proficient_summary(
        ru_strings,
        ["perception"],
        {"perception": "race"},
    )
    output = capsys.readouterr().out

    assert "Уже владеете" in output
    assert "Восприятие" in output
    assert "раса" in output


def test_normal_class_step_routes_to_subclass():
    """Normal: после класса — экран выбора архетипа."""
    from core.subclasses import subclass_offered_at_creation

    state = _creation_steps._CreationState(
        name="Hero",
        difficulty="normal",
        class_id="fighter",
    )
    assert subclass_offered_at_creation(state.difficulty, state.class_id or "")


def test_feats_step_required_for_variant_human_state():
    """Вариант человека требует шаг выбора черты после класса."""
    state = _creation_steps._CreationState(
        name="Hero",
        difficulty="normal",
        race_id="human",
        subrace_id="variant_human",
    )
    assert _creation_steps._feats_step_required(state)

    elf_state = _creation_steps._CreationState(
        name="Hero",
        difficulty="normal",
        race_id="elf",
        subrace_id="wood_elf",
    )
    assert not _creation_steps._feats_step_required(elf_state)


def test_step_after_class_choice_routes_to_feats_for_variant_human():
    state = _creation_steps._CreationState(
        name="Hero",
        difficulty="normal",
        race_id="human",
        subrace_id="variant_human",
        class_id="fighter",
    )
    assert _creation_steps._step_after_class_choice(state) == "feats"


def test_step_after_class_choice_skips_feats_for_elf():
    state = _creation_steps._CreationState(
        name="Hero",
        difficulty="normal",
        race_id="elf",
        subrace_id="wood_elf",
        class_id="fighter",
    )
    assert _creation_steps._step_after_class_choice(state) == "proficiencies"


def test_back_from_proficiencies_returns_to_feats_when_required():
    state = _creation_steps._CreationState(
        name="Hero",
        difficulty="normal",
        race_id="human",
        subrace_id="variant_human",
        class_id="fighter",
    )
    assert _creation_steps._back_step_from_proficiencies(state) == "feats"


def test_back_from_feats_returns_to_subclass_when_offered():
    """Черты после класса/подкласса — назад на подкласс, не на предысторию."""
    state = _creation_steps._CreationState(
        name="Hero",
        difficulty="normal",
        race_id="human",
        subrace_id="variant_human",
        class_id="fighter",
    )
    assert _creation_steps._back_step_from_feats(state) == "subclass"


def test_back_from_feats_returns_to_class_when_subclass_skipped():
    """Без шага подкласса назад с черт — на выбор класса."""
    state = _creation_steps._CreationState(
        name="Hero",
        difficulty="hardcore",
        race_id="human",
        subrace_id="variant_human",
        class_id="fighter",
    )
    assert _creation_steps._back_step_from_feats(state) == "class"


def test_merge_feat_languages_when_languages_empty():
    """Языки из черты добавляются, даже если список языков пуст."""
    state = _creation_steps._CreationState(
        name="Hero",
        difficulty="normal",
        languages=None,
        feat_ids=["linguist"],
        feat_choices={
            "linguist": {
                "languages": ["elvish", "dwarvish", "draconic"],
            },
        },
    )
    _creation_steps._merge_feat_languages(state)
    assert state.languages == ["elvish", "dwarvish", "draconic"]
