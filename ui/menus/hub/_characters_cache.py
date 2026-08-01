"""Кэш загрузки персонажей для hub-меню."""

from dataclasses import dataclass, field

from core.character.models import Character
from core.character.storage import LoadCharactersResult, load_characters
from core.types import StringsDict
from ui.menus.creation.corrupt_saves import show_corrupt_save_warnings_if_any


@dataclass
class CharactersLoadSession:
    """Ленивая загрузка персонажей с однократным показом предупреждений."""

    _result: LoadCharactersResult | None = field(default=None, repr=False)
    _corrupt_warning_shown: bool = field(default=False, repr=False)

    def characters(self, strings: StringsDict) -> list[Character]:
        """Список персонажей; при первом обращении — загрузка с диска."""
        if self._result is None:
            self._result = load_characters()
            self._corrupt_warning_shown = show_corrupt_save_warnings_if_any(
                strings,
                corrupt_labels=self._result.corrupt_save_warnings,
                already_shown=self._corrupt_warning_shown,
            )
        return list(self._result.characters)

    def invalidate(self) -> None:
        """Сбросить кэш после создания или удаления персонажа."""
        self._result = None
