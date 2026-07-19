---
name: dnd-mud-git-pr
description: >-
  Процедура push и PR task-ветки в dev, rename в merged/* после squash merge.
  Policy merged/* — только локально. Только по запросу пользователя. После
  dnd-mud-review.
disable-model-invocation: true
---

# dnd_mud — git PR (task → `dev`)

**Policy:** [`dnd-mud-workflow.mdc`](../../rules/dnd-mud-workflow.mdc) §`merged/*` · Overrides.  
**Оформление PR:** [`git.mdc`](~/.cursor/rules/git.mdc) §PR procedure.

## Когда выполнять

| Триггер | Действие |
|---------|----------|
| «сделай PR», push task → `dev` | §Push и PR |
| PR `MERGED` / «смержил» | §Rename в `merged/*` |
| Push без PR | Только push (§Push) |

**Предусловие:** [`dnd-mud-review`](../dnd-mud-review/SKILL.md) выполнен. Head PR — **`feat/<slug>`** после merge всех part-веток плана (если план перечислял N PR — было создано ≥ N part-веток). См. [`dnd-mud-multi-branch`](../dnd-mud-multi-branch/SKILL.md) и [`dnd-mud-workflow.mdc`](../../rules/dnd-mud-workflow.mdc) §Multi-branch.

## Push и PR

```bash
git fetch origin && git rebase origin/dev
# после rebase на remote: --force-with-lease (только своя ветка)
git push -u origin HEAD
```

Создать PR — по [`git.mdc`](~/.cursor/rules/git.mdc) §PR procedure:

1. Parallel: `git status`, `git diff`, remote tracking, `git log`, `git diff origin/dev...HEAD`
2. Draft summary по всем коммитам ветки
3. `gh pr create --base dev` с HEREDOC body

```bash
gh pr create --base dev --title "feat: …" --body "$(cat <<'EOF'
## Summary
…

## Test plan
- [ ] …

EOF
)"
```

Вернуть URL PR.

| Когда merge | Действие |
|-------------|----------|
| PR уже `MERGED` | §Rename в том же turn |
| Ещё нет | URL PR + напомнить rename; по «смержил» — rename без уточнений |

## Rename в `merged/*` (только локально)

**Запрещено:** `git push origin merged/…`, PR с head `merged/…`, upstream на `origin/merged/…`.

```bash
TASK=feat/my-task
MERGED=merged/feat/my-task
git fetch origin
git checkout dev && git pull origin dev
git push origin --delete "${TASK}" 2>/dev/null || true
if git show-ref --verify --quiet "refs/heads/${TASK}"; then
  git branch -m "${TASK}" "${MERGED}"
  git branch --unset-upstream "${MERGED}" 2>/dev/null || true
fi
git fetch origin --prune
```

`main` и `dev` не переименовывать. Префикс `merged/` не дублировать.

Если на `origin` остались legacy `merged/*` — удалить: `git push origin --delete merged/<name>`.

## Чистка part-веток (обязательный финальный шаг)

После merge всех part-веток в интеграционную (и после rename в `merged/*`) — **удалить локальные part-ветки**, слитые в `dev`, одной командой:

```bash
git fetch origin && git checkout dev && git merge --ff-only origin/dev
make branch-cleanup   # git branch -d для всех веток, слитых в CLEANUP_BASE (по умолчанию dev); merged/*, main, dev не трогает
```

Не оставлять part-ветки без префикса `merged/` — они относятся к завершённой задаче и должны быть удалены (ручной `git branch -d` на каждую — источник ошибок; используй `make branch-cleanup`). Проверка «задача завершена» — [`dnd-mud-multi-branch`](../dnd-mud-multi-branch/SKILL.md) §Проверка.
