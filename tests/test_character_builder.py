"""Тесты core/character_builder.py."""

import pytest

from core.character_builder import (
    ResolvedGrants,
    merge_languages_with_feats,
    resolve_creation_grants,
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
