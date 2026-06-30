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
        "conftest.py",
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
    "core/feat_visibility.py": ["tests/test_feats.py"],
    "core/feats_loader.py": ["tests/test_feats.py"],
    "core/character_storage.py": ["tests/test_character.py"],
    "core/scenario_actions.py": ["tests/test_scenario.py"],
    "core/levels.py": ["tests/test_progression.py"],
    "core/hp_bonuses.py": ["tests/test_progression.py"],
}

DATA_PATH_TESTS = [
    "tests/test_mod_loader.py",
    "tests/test_catalog_loader.py",
    "tests/test_io.py",
]

UI_MENU_TESTS: dict[str, str] = {
    "characters_menu": "tests/test_menus_character.py",
    "main_menu": "tests/test_menus_main.py",
    "new_game": "tests/test_menus_character.py",
    "scenario_flow": "tests/test_scenario.py",
    "settings": "tests/test_settings.py",
    "backgrounds": "tests/test_backgrounds.py",
    "languages": "tests/test_languages.py",
    "skills": "tests/test_skills.py",
    "proficiencies": "tests/test_proficiencies.py",
    "expertise": "tests/test_expertise.py",
    "asi": "tests/test_asi.py",
    "level_up": "tests/test_level_up.py",
    "class_features": "tests/test_class_features_ui.py",
    "subclass_trainer": "tests/test_subclass_trainer.py",
    "_creation_handlers": "tests/test_creation_handlers.py",
    "_deps": "tests/test_menus_character.py",
    "_common": "tests/test_menus_main.py",
}

UI_PREFIX_TESTS: list[tuple[str, str]] = [
    ("ui/menus/_creation_", "tests/test_menus_character.py"),
    ("ui/menus/_display/", "tests/test_display.py"),
    ("ui/menus/feats/", "tests/test_feats.py"),
    ("ui/menus/stats/", "tests/test_menus_stats.py"),
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
    direct = _existing_test(f"tests/test_{stem}.py")
    if direct:
        found.append(direct)
    for candidate in sorted(TESTS_DIR.glob(f"test_{stem}_*.py")):
        rel = candidate.relative_to(ROOT).as_posix()
        found.append(rel)
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

    if path.startswith(("database/", "mods/")):
        return [p for p in DATA_PATH_TESTS if _existing_test(p)]

    if path == "main.py":
        return [p for p in ["tests/test_main.py"] if _existing_test(p)]

    if path.startswith("tests/") and path.endswith(".py"):
        return [path] if _existing_test(path) else []

    if path.startswith("core/") and path.endswith(".py"):
        stem = Path(path).stem
        if stem == "__init__":
            return []
        return _glob_core_tests(stem)

    if path.startswith("ui/") and path.endswith(".py"):
        return _ui_menu_tests(path)

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
    if not py_changed:
        return [], False

    tests: set[str] = set()
    for path in py_changed:
        tests.update(source_to_tests(path))

    if not tests:
        return [], True

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
        return _run(
            [
                str(pytest),
                "--cov=core",
                "--cov=ui",
                "--cov-report=term-missing",
            ]
        )
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
