# Архив справочников Phase 2 — не загружается runtime.

Активные каталоги перенесены в runtime:

| Было (`_future/`) | Стало |
|-------------------|--------|
| `equipment/*.yaml` | [`database/equipment/`](../equipment/) |
| `core/constants.yaml` | [`database/core/constants.yaml`](../core/constants.yaml) |
| `core/abilities.yaml` | [`database/core/abilities.yaml`](../core/abilities.yaml) |
| `core/skills.yaml` | [`database/core/skills.yaml`](../core/skills.yaml) |
| `progression/feats.yaml` | [`database/progression/feats.yaml`](../progression/feats.yaml) |

Остаётся в `_future/` (не активировано):

- `core/languages.yaml` — устаревшая схема; канон — `database/core/languages.yaml`
- `core/sizes.yaml` — дублирует `constants.sizes`
- `content/mods_state.yaml` — пример состояния мода

Активные каталоги: `database/core/`, `database/backgrounds/`, `database/equipment/`, `database/progression/`.
