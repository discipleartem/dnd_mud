---
name: dnd-mud-release
description: >-
  Release checklist for dnd_mud dev to main via GitHub PR only (fetch, sync check,
  trial merge, make test, gh pr create, gh pr merge --squash). Never push/merge
  dev into main locally.
disable-model-invocation: true
---

# dnd_mud — release (`dev` → `main`)

Канон-политика: [`AGENTS.md`](../../AGENTS.md) · [`dnd-mud-workflow.mdc`](../../rules/dnd-mud-workflow.mdc) · CI: [`ci.yml`](../../.github/workflows/ci.yml), [`pr-dev-to-main-check.yml`](../../.github/workflows/pr-dev-to-main-check.yml).

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

По умолчанию **без** full bugbot `dev` vs `main` — каждая task-ветка уже прошла review при merge в `dev`.

Обязательно: `make verify` (или дождаться CI `quality`), trial merge, CI sync-check.

Full bugbot release-review ([`dnd-mud-review`](../dnd-mud-review/SKILL.md), `Base Branch: main`, ветка `dev`) — только если: (a) в release попали коммиты без task-review; (b) пользователь явно просит; (c) hotfix напрямую в `dev`.

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

`make verify` — рекомендуется локально; CI [`ci.yml`](../../.github/workflows/ci.yml) — обязателен на PR.

Создать PR (только по запросу):

```bash
gh pr create --base main --head dev --title "release: …"
```

Дождаться CI (`quality`, `dev-sync-and-mergeable`), затем squash merge PR:

```bash
gh pr merge <number> --squash
```

## После squash merge в `main`

- Action **Sync dev with main** (`.github/workflows/sync-dev-with-main.yml`) подтягивает `main` → `dev`
- При падении Action — skill `git-dev-main-sync`

## GitHub Actions

| Workflow | Триггер | Назначение |
|----------|---------|------------|
| `ci.yml` | PR → `dev`, `main` | `make check` + `make test` |
| `sync-dev-with-main.yml` | push `main` | auto merge `main` → `dev` |
| `pr-dev-to-main-check.yml` | PR `dev` → `main` | `dev` не отстаёт; пробный merge |

Ruleset `main_rules`: required checks — **`quality`**, **`dev-sync-and-mergeable`**.

Статус — панель **GitHub Actions** в Cursor / на GitHub.
