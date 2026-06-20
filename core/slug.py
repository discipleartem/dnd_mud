"""Транслитерация имён и slug для сохранений персонажей."""

import re

_CYRILLIC_TO_LATIN: dict[str, str] = {
    "а": "a",
    "б": "b",
    "в": "v",
    "г": "g",
    "д": "d",
    "е": "e",
    "ё": "yo",
    "ж": "zh",
    "з": "z",
    "и": "i",
    "й": "y",
    "к": "k",
    "л": "l",
    "м": "m",
    "н": "n",
    "о": "o",
    "п": "p",
    "р": "r",
    "с": "s",
    "т": "t",
    "у": "u",
    "ф": "f",
    "х": "kh",
    "ц": "ts",
    "ч": "ch",
    "ш": "sh",
    "щ": "shch",
    "ъ": "",
    "ы": "y",
    "ь": "",
    "э": "e",
    "ю": "yu",
    "я": "ya",
}


def _transliterate(text: str) -> str:
    """Транслитерировать кириллицу в латиницу."""
    result: list[str] = []
    for char in text:
        lower = char.lower()
        if lower in _CYRILLIC_TO_LATIN:
            mapped = _CYRILLIC_TO_LATIN[lower]
            if char.isupper() and mapped:
                mapped = mapped[0].upper() + mapped[1:]
            result.append(mapped)
        else:
            result.append(char)
    return "".join(result)


def make_save_slug(name: str) -> str:
    """Построить slug из имени персонажа."""
    transliterated = _transliterate(name).lower()
    slug = re.sub(r"[^a-z0-9]+", "_", transliterated)
    slug = slug.strip("_")
    return slug or "character"
