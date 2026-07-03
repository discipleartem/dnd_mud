# Devin IDE Rules — dnd_mud

Адаптация локальных правил Cursor IDE для Devin IDE. Оригинальные правила Cursor сохранены в `.cursor/`.

## Структура

```
.devin/
├── README.md                    # Этот файл
├── rules/                       # Локальные правила проекта
│   ├── 00-project.md           # Stack, команды, docs index
│   ├── dnd-mud-workflow.md     # Git/verify/review overrides
│   ├── dnd-mud-core.md         # Слои, локализация, D&D механика
│   ├── dnd-mud-data.md         # YAML/JSON conventions
│   ├── dnd-mud-python.md       # Python 3.12, KISS, типизация
│   └── dnd-mud-tests.md        # Pytest, бюджет на PR
└── workflows/                   # Процедуры и workflows
    ├── README.md               # Индекс workflows
    ├── dnd-mud-docs-after-task.md
    ├── dnd-mud-verify.md
    ├── dnd-mud-verify/
    │   └── reference.md
    ├── dnd-mud-review.md
    ├── dnd-mud-review/
    │   ├── checklist-full.md
    │   └── template-findings.md
    ├── dnd-mud-fix-plan.md
    ├── dnd-mud-git-pr.md
    └── dnd-mud-release.md
```

## Отличия от Cursor

1. **Формат файлов:** `.mdc` (Cursor) → `.md` (Devin)
2. **Ссылки на глобальные правила:** Убраны абсолютные пути к глобальным правилам Cursor (`~/.cursor/rules/`), заменены на относительные ссылки или описания
3. **Frontmatter:** Сохранён `description` и `alwaysApply`/`globs` для совместимости
4. **Skills → Workflows:** Cursor skills адаптированы в Devin workflows

## Использование

Devin IDE автоматически загружает правила из `.devin/rules/` при работе с проектом.

Для запуска workflows используйте соответствующие команды Devin IDE или следуйте процедурам из файлов в `.devin/workflows/`.

## Синхронизация с Cursor

При обновлении правил в `.cursor/rules/` или `.cursor/skills/` необходимо вручную синхронизировать изменения в `.devin/`:

1. Проверить изменения в `.cursor/`
2. Обновить соответствующие файлы в `.devin/rules/` и `.devin/workflows/`
3. Сохранить формат `.md` и адаптировать ссылки

## Ссылки

- Оригинальные правила Cursor: `.cursor/rules/`
- Оригинальные skills Cursor: `.cursor/skills/`
- Project docs: `docs/`
- Agent orchestration: `AGENTS.md`
