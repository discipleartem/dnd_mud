"""Тесты core/character_builder.py."""

from core.character_builder import (
    ResolvedGrants,
    merge_languages_with_feats,
    resolve_creation_grants,
)


def test_resolve_creation_grants_fighter_human_acolyte() -> None:
    grants = resolve_creation_grants(
        "human",
        "standard",
        "fighter",
        "acolyte",
        "champion",
        1,
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


def test_resolve_creation_grants_variant_human_extra_skills() -> None:
    base = resolve_creation_grants(
        "human",
        "variant_human",
        "rogue",
        None,
        None,
        1,
        include_feat_languages=False,
    )
    with_extra = resolve_creation_grants(
        "human",
        "variant_human",
        "rogue",
        None,
        None,
        1,
        extra_skills=["stealth"],
        include_feat_languages=False,
    )
    assert "stealth" in with_extra.skill_ids
    assert len(with_extra.skill_ids) >= len(base.skill_ids)


def test_merge_languages_with_feats_dedupes() -> None:
    merged = merge_languages_with_feats(
        ["common"],
        ["linguist"],
        {"linguist": {"languages": ["elvish", "common"]}},
    )
    assert merged.count("common") == 1
    assert "elvish" in merged


def test_build_fixed_proficiencies_delegates_to_builder() -> None:
    from core.proficiencies import build_fixed_proficiencies

    weapons, armors, tools = build_fixed_proficiencies(
        "dwarf",
        "mountain_dwarf",
        "fighter",
        None,
        None,
        1,
    )
    grants = resolve_creation_grants(
        "dwarf",
        "mountain_dwarf",
        "fighter",
        None,
        None,
        1,
        include_feat_languages=False,
    )
    assert weapons == list(grants.weapon_tokens)
    assert armors == list(grants.armor_tokens)
    assert tools == list(grants.tool_tokens)
