# Bugbot checklist — full review

**Base Branch:** `<dev|main>` (из workflow)

## Correctness

- [ ] Логика соответствует требованиям / ticket
- [ ] Нет очевидных багов (off-by-one, None errors, type mismatches)
- [ ] Обработка ошибок и edge cases
- [ ] D&D механика соответствует PHB / [`docs/rules/`](../../docs/rules/)

## Code quality

- [ ] KISS: нет лишних абстракций, фабрик, стратегий для 1–2 вариантов
- [ ] Типы: type hints на публичных функциях, `core/`
- [ ] Имена: понятные, не сокращения без контекста
- [ ] Дублирование: нет копипасты логики (DRY)

## Testing

- [ ] Тесты на изменённое поведение (не «на всякий случай»)
- [ ] Бюджет на PR соблюдён (≤ 3–5 для фичи, 1 для багфикса)
- [ ] Нет дублирования одного сценария в 3+ файлах
- [ ] Golden-path helpers используются, не копируются

## Data / YAML

- [ ] YAML для справочников, JSON для сейвов/конфигов
- [ ] `ru` и `en` синхронизированы
- [ ] Schema version при изменении формата JSON
- [ ] Нет хардкода игровых данных в Python

## Documentation

- [ ] `docs/API.md` обновлён для публичных функций
- [ ] `docs/ARCHITECTURE.md` для новых слоёв/модулей
- [ ] `docs/DND_RULES.md` для новой механики
- [ ] `docs/CHANGELOG.md` для заметных фич/фиксов
- [ ] Не дублируется код в docs — ссылки достаточно

## Git hygiene

- [ ] Commits atomic, не смешивают unrelated (код vs docs vs `.devin/`)
- [ ] Commit messages Conventional Commits, английский
- [ ] Не закоммичено `.coverage`, `saves/`
- [ ] Part-ветки слиты `--no-ff` и удалены (если план с N PR)

## Performance / security

- [ ] Нет очевидных проблем (N+1, утечки памяти)
- [ ] Валидация пользовательского ввода
- [ ] Безопасная обработка файлов (пути, permissions)

## UI (если в diff)

- [ ] Локализация через `get_string`, не хардкод
- [ ] UI не читает/пишет данные напрямую
- [ ] Smoke `python main.py` пройден
