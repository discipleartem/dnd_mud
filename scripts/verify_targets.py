#!/usr/bin/env python3
"""Разрешение целей verify (lint / pytest) по git diff."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TESTS_DIR = ROOT / "tests"

FULL_SUITE_PATHS = frozenset(
    {
        "pyproject.toml",
        "scripts/verify_targets.py",
        "Makefile",
    }
)

CROSS_CUTTING_MODULES = frozenset(
    {
        "core/types.py",
        "core/__init__.py",
        "ui/__init__.py",
    }
)

CORE_MODULE_TESTS: dict[str, list[str]] = {
    "core/feats/catalog.py": ["tests/core/feats/test_feats.py"],
    "core/feats/apply.py": ["tests/core/feats/test_feats.py"],
    "core/feats/text.py": ["tests/core/feats/test_feats.py"],
    "core/feats/requirements.py": ["tests/core/feats/test_feats.py"],
    "core/character/storage.py": ["tests/core/character/test_character.py"],
    "core/grants/normalize.py": ["tests/core/grants/test_grants.py"],
    "core/catalogs/classes.py": [
        "tests/core/progression/test_subclasses.py",
        "tests/core/mechanics/test_proficiencies.py",
    ],
    "core/progression/xp_levels.py": [
        "tests/core/progression/test_progression.py"
    ],
    "core/progression/hp.py": ["tests/core/progression/test_progression.py"],
    "core/progression/asi.py": ["tests/core/progression/test_asi.py"],
    "core/progression/class_progression.py": [
        "tests/core/progression/test_progression.py"
    ],
    "core/progression/level_up.py": [
        "tests/core/progression/test_progression.py"
    ],
    "core/inventory/items.py": ["tests/core/inventory/test_inventory.py"],
    "core/inventory/armor_class.py": [
        "tests/core/inventory/test_inventory.py"
    ],
    "core/inventory/equip_defaults.py": [
        "tests/core/inventory/test_inventory.py"
    ],
    "core/inventory/starting_equipment.py": [
        "tests/core/inventory/test_starting_equipment.py"
    ],
    "core/inventory/starting_equipment_labels.py": [
        "tests/core/inventory/test_starting_equipment_labels.py"
    ],
    "core/mechanics/proficiencies.py": [
        "tests/core/mechanics/test_proficiencies.py"
    ],
    "core/mechanics/proficiency_collect.py": [
        "tests/core/mechanics/test_proficiencies.py"
    ],
    "core/mechanics/dice.py": ["tests/core/mechanics/test_stats.py"],
    "core/constants.py": ["tests/core/mechanics/test_stats.py"],
    "core/engine/difficulty.py": ["tests/core/mechanics/test_stats.py"],
    "core/catalogs/races.py": ["tests/core/grants/test_grants.py"],
    "core/catalogs/adventure.py": ["tests/core/character/test_models.py"],
    "core/catalogs/backgrounds.py": ["tests/core/character/test_models.py"],
    "core/platform/mod_loader.py": [
        "tests/core/platform/test_catalog_loader.py"
    ],
    "core/platform/catalog_session.py": [
        "tests/core/platform/test_catalog_loader.py"
    ],
    "core/catalogs/skills.py": ["tests/core/mechanics/test_proficiencies.py"],
    "core/platform/settings.py": ["tests/ui/test_menus_main.py"],
    "core/engine/scenario_actions.py": [
        "tests/core/character/test_models.py",
        "tests/core/progression/test_class_features.py",
    ],
    "core/engine/game_engine.py": ["tests/core/engine/test_game_engine.py"],
    "core/engine/combat/rolls.py": ["tests/core/engine/test_phase2_engine.py"],
}

CORE_PACKAGE_PREFIX_TESTS: list[tuple[str, list[str]]] = [
    ("core/feats/", ["tests/core/feats/test_feats.py"]),
    ("core/grants/", ["tests/core/grants/test_grants.py"]),
    ("core/progression/", ["tests/core/progression/test_progression.py"]),
    ("core/inventory/", ["tests/core/inventory/test_inventory.py"]),
    ("core/character/", ["tests/core/character/test_character.py"]),
    ("core/catalogs/", ["tests/core/platform/test_catalog_loader.py"]),
    ("core/platform/", ["tests/core/platform/test_catalog_loader.py"]),
    ("core/mechanics/", ["tests/core/mechanics/test_stats.py"]),
    ("core/engine/", ["tests/core/engine/test_game_engine.py"]),
]

DATA_PATH_TESTS = [
    "tests/core/platform/test_catalog_loader.py",
    "tests/data/test_data_schema.py",
    "tests/core/platform/test_io.py",
]

UI_MENU_TESTS: dict[str, str] = {
    "characters_menu": "tests/ui/test_menus_characters_hub.py",
    "main_menu": "tests/ui/test_menus_main.py",
    "new_game": "tests/ui/test_menus_new_game.py",
    "flow": "tests/core/progression/test_progression.py",
    "settings": "tests/ui/test_menus_main.py",
    "backgrounds": "tests/core/character/test_models.py",
    "languages": "tests/core/catalogs/test_languages.py",
    "skills": "tests/core/mechanics/test_proficiencies.py",
    "proficiencies": "tests/core/mechanics/test_proficiencies.py",
    "expertise": "tests/core/mechanics/test_expertise.py",
    "asi": "tests/core/progression/test_asi.py",
    "level_up": "tests/core/progression/test_progression.py",
    "class_features": "tests/core/progression/test_class_features.py",
    "subclass_trainer": "tests/core/progression/test_subclasses.py",
    "console": "tests/ui/test_menus_main.py",
    "steps": "tests/ui/test_menus_creation.py",
    "handlers": "tests/ui/test_menus_creation.py",
}

UI_PREFIX_TESTS: list[tuple[str, str]] = [
    ("ui/menus/creation/", "tests/ui/test_menus_creation.py"),
    ("ui/menus/hub/", "tests/ui/test_menus_main.py"),
    ("ui/menus/progression/", "tests/core/progression/test_progression.py"),
    ("ui/menus/scenario/", "tests/core/progression/test_progression.py"),
    ("ui/menus/display/", "tests/core/inventory/test_equipment.py"),
    ("ui/menus/feats/", "tests/core/feats/test_feats.py"),
    ("ui/menus/stats/", "tests/ui/test_menus_stats.py"),
]


def _git_changed_paths(mode: str, base: str) -> list[str]:
    if mode == "staged":
        cmd = ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"]
    elif mode == "scope":
        cmd = [
            "git",
            "diff",
            "--name-only",
            "--diff-filter=ACM",
            f"{base}...HEAD",
        ]
    else:
        msg = f"unknown mode: {mode}"
        raise ValueError(msg)
    result = subprocess.run(
        cmd,
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [
        line.strip() for line in result.stdout.splitlines() if line.strip()
    ]


def _existing_test(path: str) -> str | None:
    full = ROOT / path
    return path if full.is_file() else None


def _glob_core_tests(stem: str) -> list[str]:
    found: list[str] = []
    for candidate in sorted(TESTS_DIR.rglob(f"test_{stem}.py")):
        found.append(candidate.relative_to(ROOT).as_posix())
    for candidate in sorted(TESTS_DIR.rglob(f"test_{stem}_*.py")):
        found.append(candidate.relative_to(ROOT).as_posix())
    return found


def _ui_menu_tests(path: str) -> list[str]:
    rel = Path(path)
    if rel.parts[0] != "ui":
        return []

    found: list[str] = []
    if len(rel.parts) >= 2 and rel.parts[1] == "menus":
        name = rel.stem
        if name in UI_MENU_TESTS and (
            existing := _existing_test(UI_MENU_TESTS[name])
        ):
            found.append(existing)

        for prefix, test_path in UI_PREFIX_TESTS:
            if (
                path.startswith(prefix)
                and (existing := _existing_test(test_path))
                and existing not in found
            ):
                found.append(existing)

        if not found:
            menu_test = _existing_test(f"tests/test_menus_{name}.py")
            if menu_test:
                found.append(menu_test)

    if not found:
        ui_test = _existing_test(f"tests/test_{rel.stem}.py")
        if ui_test:
            found.append(ui_test)
    return found


def source_to_tests(path: str) -> list[str]:
    """Сопоставить изменённый путь с pytest-файлами."""
    if path in FULL_SUITE_PATHS or path.endswith("/conftest.py"):
        return []

    if path in CROSS_CUTTING_MODULES:
        return []

    if path in CORE_MODULE_TESTS:
        return [
            p for p in CORE_MODULE_TESTS[path] if _existing_test(p) is not None
        ]

    for prefix, tests in CORE_PACKAGE_PREFIX_TESTS:
        if path.startswith(prefix) and path.endswith(".py"):
            return [p for p in tests if _existing_test(p) is not None]

    if path.startswith(("database/", "mods/")):
        return [p for p in DATA_PATH_TESTS if _existing_test(p)]

    if path.startswith("tests/") and path.endswith(".py"):
        return [path] if _existing_test(path) else []

    if path.startswith("core/") and path.endswith(".py"):
        stem = Path(path).stem
        if stem == "__init__":
            return []
        return _glob_core_tests(stem)

    if path.startswith("ui/") and path.endswith(".py"):
        return _ui_menu_tests(path)

    if path == "main.py":
        return _glob_core_tests("menus_main")

    return []


def requires_full_suite(changed: list[str]) -> bool:
    """Нужен полный прогон test/check."""
    if not changed:
        return False
    for path in changed:
        if path in FULL_SUITE_PATHS:
            return True
        if path.endswith("/conftest.py") or path == "tests/conftest.py":
            return True
        if path in CROSS_CUTTING_MODULES:
            return True
    return False


def resolve_lint_paths(changed: list[str]) -> tuple[list[str], bool]:
    """(.py для lint, full_suite)."""
    if requires_full_suite(changed):
        return [], True
    lint = sorted(
        {
            path
            for path in changed
            if path.endswith(".py") and (ROOT / path).is_file()
        }
    )
    return lint, False


def resolve_test_paths(changed: list[str]) -> tuple[list[str], bool]:
    """(pytest files, full_suite)."""
    if requires_full_suite(changed):
        return [], True

    py_changed = [p for p in changed if p.endswith(".py")]
    data_changed = [
        p
        for p in changed
        if p.startswith(("database/", "mods/")) and not p.endswith(".py")
    ]

    if not py_changed and data_changed:
        data_tests = [p for p in DATA_PATH_TESTS if _existing_test(p)]
        return sorted(data_tests), False

    if not py_changed:
        return [], False

    tests: set[str] = set()
    for path in py_changed:
        mapped = source_to_tests(path)
        if not mapped:
            return [], True
        tests.update(mapped)

    return sorted(tests), False


def _run(cmd: list[str]) -> int:
    print("+", " ".join(cmd), flush=True)
    return subprocess.run(cmd, cwd=ROOT).returncode


def cmd_resolve_tests(args: argparse.Namespace) -> int:
    paths, full = resolve_test_paths(_git_changed_paths(args.mode, args.base))
    if full:
        print("__FULL__")
        return 0
    if not paths:
        print("__SKIP__")
        return 0
    for path in paths:
        print(path)
    return 0


def cmd_resolve_lint(args: argparse.Namespace) -> int:
    paths, full = resolve_lint_paths(_git_changed_paths(args.mode, args.base))
    if full:
        print("__FULL__")
        return 0
    if not paths:
        print("__SKIP__")
        return 0
    for path in paths:
        print(path)
    return 0


def cmd_run_test(args: argparse.Namespace) -> int:
    paths, full = resolve_test_paths(_git_changed_paths(args.mode, args.base))
    pytest = ROOT / ".venv" / "bin" / "pytest"
    if not pytest.is_file():
        print(
            "verify_targets: нет .venv/bin/pytest — make install",
            file=sys.stderr,
        )
        return 1
    if full:
        return _run([str(pytest)])
    if not paths:
        print("verify_targets: нет тестов для diff — skip")
        return 0
    return _run([str(pytest), *paths])


def cmd_run_check(args: argparse.Namespace) -> int:
    paths, full = resolve_lint_paths(_git_changed_paths(args.mode, args.base))
    venv = ROOT / ".venv" / "bin"
    ruff = venv / "ruff"
    black = venv / "black"
    mypy = venv / "mypy"
    for tool in (ruff, black, mypy):
        if not tool.is_file():
            print(
                f"verify_targets: нет {tool} — make install",
                file=sys.stderr,
            )
            return 1
    if full:
        code = _run([str(ruff), "check", "."])
        if code:
            return code
        code = _run([str(black), "--check", "."])
        if code:
            return code
        return _run([str(mypy), "."])
    if not paths:
        print("verify_targets: нет .py для check — skip")
        return 0
    code = _run([str(ruff), "check", *paths])
    if code:
        return code
    code = _run([str(black), "--check", *paths])
    if code:
        return code
    return _run([str(mypy), *paths])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("staged", "scope"),
        default="staged",
        help="staged — index; scope — BASE...HEAD",
    )
    parser.add_argument(
        "--base",
        default="origin/dev",
        help="base ref для mode=scope",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("resolve-tests", help="вывести pytest-файлы")
    sub.add_parser("resolve-lint", help="вывести .py для lint")
    sub.add_parser("run-test", help="запустить pytest")
    sub.add_parser("run-check", help="запустить ruff/black/mypy")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handlers = {
        "resolve-tests": cmd_resolve_tests,
        "resolve-lint": cmd_resolve_lint,
        "run-test": cmd_run_test,
        "run-check": cmd_run_check,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
