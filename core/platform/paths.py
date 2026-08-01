"""Канонические пути к файлам данных и сохранений."""

from pathlib import Path

# database/
CONSTANTS_FILE = Path("database/core/constants.yaml")
ABILITIES_FILE = Path("database/core/abilities.yaml")
SKILLS_FILE = Path("database/core/skills.yaml")
LANGUAGES_FILE = Path("database/core/languages.yaml")
SETTINGS_PATH = Path("database/core/settings.json")
MODS_STATE_FILE = Path("database/core/mods_state.json")

RACES_FILE = Path("database/races/races.yaml")
CLASSES_FILE = Path("database/classes/classes.yaml")
BACKGROUNDS_FILE = Path("database/backgrounds/backgrounds.yaml")

WEAPONS_FILE = Path("database/equipment/weapon.yaml")
ARMOR_FILE = Path("database/equipment/armor.yaml")
TOOLS_FILE = Path("database/equipment/tools.yaml")
EQUIPMENT_FILE = Path("database/equipment/equipment.yaml")

FEATS_FILE = Path("database/progression/feats.yaml")
ADVENTURES_FILE = Path("database/content/adventures.yaml")

STRINGS_DIR = Path("database/strings")

# saves/
SAVES_DIR = Path("saves")
SESSIONS_DIR = SAVES_DIR / "sessions"
CREATION_DRAFT_PATH = SAVES_DIR / "creation_draft.json"

# mods/
MODS_DIR = Path("mods")
