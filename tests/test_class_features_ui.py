"""Тесты UI применения особенностей класса."""

from core.models import Character
from ui.menus.class_features import apply_pending_class_features


def test_apply_pending_class_features_champion_marks_applied(
    monkeypatch, ru_strings
):
    """Чемпион без выборов — особенности отмечены применёнными."""
    char = Character(
        name="Hero",
        race="human",
        class_id="fighter",
        level=3,
        subclass_id="champion",
        class_features_applied=False,
        difficulty="normal",
    )
    monkeypatch.setattr(
        "ui.menus.class_features._deps.update_character",
        lambda c: c,
    )
    monkeypatch.setattr(
        "ui.menus.class_features._print_success_and_wait",
        lambda *args, **kwargs: None,
    )

    result = apply_pending_class_features(ru_strings, char, "ru")
    assert result is not None
    assert result.class_features_applied is True


def test_apply_pending_class_features_noop_when_not_needed(ru_strings):
    """Особенности не требуются — персонаж возвращается без изменений."""
    char = Character(
        name="Hero",
        race="elf",
        class_id="fighter",
        level=1,
        difficulty="normal",
    )
    result = apply_pending_class_features(ru_strings, char, "ru")
    assert result is char
