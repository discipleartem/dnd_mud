---
name: dnd-mud-release
description: >-
  Release checklist for dnd_mud dev to main via GitHub PR only (fetch, sync check,
  trial merge, make test, gh pr create, gh pr merge --squash). Never push/merge
  dev into main locally.
disable-model-invocation: true
---

# dnd_mud — release (`dev` → `main`)

Канон-политика: [`AGENTS.md`](../../AGENTS.md) §8 · [`dnd-mud-git.mdc`](../../rules/dnd-mud-git.mdc) · CI: `.github/workflows/pr-dev-to-main-check.yml`.

## Когда выполнять

По запросу пользователя: release `dev` → `main`.

## Политика (обязательно)

**Все** релизы `dev` → `main` — **только через GitHub PR**. Без PR в `main` не попадает.

| Разрешено | Запрещено |
|-----------|-----------|
| `gh pr create --base main --head dev` → CI → `gh pr merge --squash` | Локальный `git checkout main && git merge dev && git push` |
| Squash merge PR на GitHub (или `gh pr merge --squash`) | `git push origin main` напрямую с коммитами из `dev` |
| | Fast-forward / merge `dev` в `main` в обход PR |

Пробный merge (`git merge origin/main --no-commit --no-ff`) — только локальная проверка, **не** способ релиза.

## Перед PR

Review (skill [`dnd-mud-review`](../dnd-mud-review/SKILL.md)): локальный subagent, `Base Branch: main`, ветка `dev` — **один раз**, **до** создания release PR (GitHub PR Bugbot не используется).

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

Дождаться CI (`dev-sync-and-mergeable`), затем squash merge PR:

```bash
gh pr merge <number> --squash
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
