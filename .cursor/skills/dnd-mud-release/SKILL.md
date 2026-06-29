---
name: dnd-mud-release
description: >-
  Release checklist for dnd_mud dev to main PR (fetch, sync check, trial merge,
  make test, gh pr create). Use for release PR, dev to main merge, or squash
  release workflow.
disable-model-invocation: true
---

# dnd_mud — release (`dev` → `main`)

Канон-политика: [`dnd-mud-verify.mdc`](.cursor/rules/dnd-mud-verify.mdc) §Release · CI: `.github/workflows/pr-dev-to-main-check.yml`.

## Когда выполнять

По запросу пользователя: PR `dev` → `main`, релиз, squash merge в `main`.

## Перед PR

Review (skill [`dnd-mud-review`](../dnd-mud-review/SKILL.md)): readonly Bugbot, `Base Branch: main`, ветка `dev` — **до** создания release PR.

```bash
source .venv/bin/activate
git fetch origin
git checkout dev && git pull origin dev
git log dev..origin/main --oneline   # must be empty
```

Если не пуст — сначала skill `git-dev-main-sync` (или [`git-dev-main-sync.md`](~/.cursor/docs/git-dev-main-sync.md)).

Пробный merge без коммита:

```bash
git merge origin/main --no-commit --no-ff && git merge --abort
```

`make test` — обязательно.

Создать PR (только по запросу):

```bash
gh pr create --base main --head dev --title "release: …"
```

## После squash merge в `main`

- Action **Sync dev with main** (`.github/workflows/sync-dev-with-main.yml`) подтягивает `main` → `dev`
- При падении Action — skill `git-dev-main-sync`

## GitHub Actions

| Workflow | Триггер | Назначение |
|----------|---------|------------|
| `sync-dev-with-main.yml` | push `main` | auto merge `main` → `dev` |
| `pr-dev-to-main-check.yml` | PR `dev` → `main` | `dev` не отстаёт; пробный merge |

Orphaned workflows на GitHub без файла в репо — `gh workflow disable "<name>"`.

Ruleset `main_rules`: required check — **`dev-sync-and-mergeable`** (job name).

Статус — панель **GitHub Actions** в Cursor / на GitHub.
