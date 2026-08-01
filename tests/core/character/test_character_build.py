"""Тесты core/character_build.py."""

import pytest

from core.character.build import (
    CreationContext,
    ResolvedGrants,
    merge_languages_with_feats,
    resolve_creation_grants,
    resolve_grants_for_context,
)
from tests.creation_helpers import fighter_acolyte_creation

pytestmark = pytest.mark.usefixtures("catalog_caches_cleared")


def test_resolve_creation_grants_fighter_human_acolyte() -> None:
    ctx = fighter_acolyte_creation()
    grants = resolve_creation_grants(
        ctx["race_id"],
        ctx["subrace_id"],
        ctx["class_id"],
        ctx["background_id"],
        ctx["subclass_id"],
        ctx["level"],
    )
    assert isinstance(grants, ResolvedGrants)
    assert "simple" in grants.weapon_tokens
    assert "martial" in grants.weapon_tokens
    assert "insight" in grants.skill_ids
    assert "religion" in grants.skill_ids


def test_resolve_creation_grants_includes_feat_proficiencies() -> None:
    grants = resolve_creation_grants(
        "human",
        "standard",
        "fighter",
        None,
        None,
        1,
        feat_ids=["tough"],
        include_feat_languages=False,
    )
    assert grants.weapon_tokens
    assert grants.armor_tokens


def test_merge_languages_with_feats_dedupes() -> None:
    merged = merge_languages_with_feats(
        ["common"],
        ["linguist"],
        {"linguist": {"languages": ["elvish", "common"]}},
    )
    assert merged.count("common") == 1
    assert "elvish" in merged


def test_resolve_grants_for_context_merges_extra_skills() -> None:
    ctx = fighter_acolyte_creation()
    creation_ctx = CreationContext(
        race_id=ctx["race_id"],
        subrace_id=ctx["subrace_id"],
        class_id=ctx["class_id"],
        background_id=ctx["background_id"],
        subclass_id=ctx["subclass_id"],
        level=ctx["level"],
        extra_skills=("athletics",),
    )
    grants = resolve_grants_for_context(
        creation_ctx, include_feat_languages=False
    )
    assert "athletics" in grants.skill_ids
    assert "insight" in grants.skill_ids
