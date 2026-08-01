"""Отображение и подтверждение требований черт."""

from typing import Any

from colorama import Fore, Style

from core.feats.requirement_text import (
    _format_or_ability_requirements,
    _format_requirement_text,
    _split_feat_requirements,
)
from core.feats.requirements import (
    FeatRequirementContext,
    requirement_met,
)
from core.feats.text import (
    feat_full_description_lines,
    feat_summary_description,
)
from core.platform.localization import get_string
from core.types import StringsDict
from ui.menus.console import (
    confirm_yes_no,
    print_screen_header,
)


def _requirement_line_color(met: bool, *, muted: bool) -> str:
    """Цвет строки требования: зелёный/красный при muted, иначе цвет секции."""
    if not muted:
        return str(Fore.GREEN)
    return str(Fore.GREEN if met else Fore.RED)


def _print_feat_requirements(
    strings: StringsDict,
    feat: dict[str, Any],
    ctx: FeatRequirementContext,
    language: str,
    *,
    muted: bool,
    section_color: str,
) -> None:
    """Список требований черты с отметкой выполнения."""
    and_reqs, or_reqs = _split_feat_requirements(feat)
    if not and_reqs and not or_reqs:
        return
    line_count = len(and_reqs) + (1 if or_reqs else 0)
    label_key = (
        "character.feat_requirement_label"
        if line_count == 1
        else "character.feat_requirements_label"
    )
    print(
        f"     {section_color}"
        f"{get_string(strings, label_key)}"
        f"{Style.RESET_ALL}"
    )
    for req in and_reqs:
        text = _format_requirement_text(strings, req, ctx, language)
        if not text:
            continue
        met = requirement_met(req, ctx)
        color = _requirement_line_color(met, muted=muted)
        print(f"     {color}• {text}{Style.RESET_ALL}")
    if or_reqs:
        line = _format_or_ability_requirements(strings, or_reqs)
        met_any = any(requirement_met(req, ctx) for req in or_reqs)
        if line is None:
            parts: list[str] = []
            for req in or_reqs:
                text = _format_requirement_text(strings, req, ctx, language)
                if text:
                    parts.append(text)
            if parts:
                or_sep = get_string(strings, "character.feat_req_or_sep")
                line = or_sep.join(parts)
        if line:
            color = _requirement_line_color(met_any, muted=muted)
            print(f"     {color}• {line}{Style.RESET_ALL}")


def _print_feat_details(
    strings: StringsDict,
    feat: dict[str, Any],
    ctx: FeatRequirementContext,
    language: str,
    *,
    color: str = Fore.CYAN,
    muted: bool = False,
) -> None:
    """Имя, описание и требования черты."""
    print(f"  {color}{Style.BRIGHT}{feat.get('name', '?')}{Style.RESET_ALL}")
    desc = feat_summary_description(feat)
    if desc:
        print(f"     {color}{desc}{Style.RESET_ALL}")
    _print_feat_requirements(
        strings, feat, ctx, language, muted=muted, section_color=color
    )


def _print_feat_full_description(
    strings: StringsDict,
    feat: dict[str, Any],
    ctx: FeatRequirementContext,
    language: str,
) -> None:
    """Экран полного описания выбранной черты."""
    print_screen_header(get_string(strings, "character.feat_detail_caption"))
    name = str(feat.get("name", "?"))
    print(f"  {Fore.CYAN}{Style.BRIGHT}{name}{Style.RESET_ALL}")
    print()
    intro = feat_summary_description(feat)
    if intro:
        print(f"  {intro}")
        print()
    for line in feat_full_description_lines(feat):
        if line.strip():
            print(f"  {line}")
        else:
            print()
    _print_feat_requirements(
        strings,
        feat,
        ctx,
        language,
        muted=False,
        section_color=Fore.CYAN,
    )
    print()


def _confirm_feat_selection(
    strings: StringsDict,
    feat: dict[str, Any],
    ctx: FeatRequirementContext,
    language: str,
) -> bool:
    """Показать полное описание и подтвердить выбор."""
    _print_feat_full_description(strings, feat, ctx, language)
    return confirm_yes_no(strings, "character.feat_confirm_prompt")
