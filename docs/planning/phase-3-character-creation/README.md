# Phase 3: Создание персонажа

## Обзор

Система создания персонажей для D&D Text MUD, следующая правилам D&D 5e.

## Структура подзадач

### 1. Выбор расы
- Сервис рас (RaceService)
- UI выбора расы (RaceSelectionAdapter)
- Применение расовых бонусов
- **Детали:** [1-race-selection.md](1-race-selection.md)

### 2. Генерация характеристик  
- Сервис характеристик (AbilitiesService)
- UI характеристик (AbilitiesGenerationAdapter)
- Три метода генерации
- **Детали:** [2-abilities-generation.md](2-abilities-generation.md)

### 3. Выбор класса
- Сервис классов (ClassService)
- UI выбора класса (ClassSelectionAdapter)
- Проверка требований характеристик
- **Детали:** [3-class-selection.md](3-class-selection.md)

### 4. Выбор навыков
- Сервис навыков (SkillsService)
- UI выбора навыков (SkillsSelectionAdapter)
- Применение бонусов от расы/класса
- **Детали:** [4-skills-selection.md](4-skills-selection.md)

## Интеграция

Все подзадачи объединяются через:
- CharacterCreationService (основная логика)
- CharacterCreationAdapter (UI слой)
- Пошаговая навигация между этапами

---

*Этот этап будет реализован после завершения Phase 2.*
