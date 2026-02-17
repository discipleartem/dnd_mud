# Архитектура D&D MUD - Чистая Архитектура

Проект D&D MUD реализован с использованием **Чистой Архитектуры** (Clean Architecture) Роберта Мартина. Этот документ описывает текущую реализацию и архитектурные решения.

## 🏛️ Обзор архитектуры

### 4 слоя Чистой Архитектуры

```
┌─────────────────────────────────────────────────────────────┐
│                    Infrastructure Layer                      │
│  (UI, Database, External APIs, Frameworks)              │
├─────────────────────────────────────────────────────────────┤
│                  Interface Adapters Layer                   │
│        (Controllers, Presenters, Repositories)              │
├─────────────────────────────────────────────────────────────┤
│                 Application Layer (Use Cases)               │
│              (Business Logic Orchestration)                 │
├─────────────────────────────────────────────────────────────┤
│                    Domain Layer                            │
│         (Entities, Value Objects, Business Rules)           │
└─────────────────────────────────────────────────────────────┘
```

### Dependency Rule

**Зависимости направлены только внутрь:**

- Domain → ничего не зависит
- Application → Domain
- Adapters → Application + Domain  
- Infrastructure → Adapters + Application + Domain

## 📁 Текущая структура проекта

```
src/
├── domain/                    # Enterprise Business Rules
│   ├── entities/             # Character, Race, Class
│   │   ├── character.py      # Основная сущность персонажа
│   │   ├── race.py          # Расы D&D
│   │   ├── class_.py        # Классы D&D
│   │   ├── attribute.py     # Характеристики
│   │   ├── skill.py         # Навыки
│   │   └── saving_throw.py  # Спасброски
│   ├── value_objects/        # Dice, Attributes, Skills
│   │   └── dice.py          # Система бросков кубиков
│   ├── services/             # CharacterGeneration
│   │   └── character_generation.py # Генерация персонажей
│   ├── repositories/         # Интерфейсы репозиториев
│   └── interfaces/          # Интерфейсы для внешних систем
│       └── localization.py # Интерфейс локализации
├── application/               # Application Business Rules
│   ├── use_cases/           # CreateCharacter, LoadGame
│   ├── dto/                 # Data Transfer Objects
│   └── interfaces/          # Интерфейсы для адаптеров
├── adapters/                # Interface Adapters
│   ├── repositories/        # Реализации репозиториев
│   │   └── character_repository.py # YAML хранение персонажей
│   ├── presenters/          # Презентеры
│   ├── controllers/         # Контроллеры
│   └── gateways/           # Шлюзы к внешним системам
│       ├── localization/     # Адаптеры локализации
│       └── localization_adapter.py
└── infrastructure/          # Frameworks & Drivers
    ├── ui/                 # Консольный интерфейс
    │   ├── menus/            # Меню игры
    │   │   ├── main_menu.py
    │   │   ├── character_creation.py
    │   │   └── character_menu.py
    │   ├── renderer.py       # Рендеринг консоли
    │   └── input_handler.py  # Обработка ввода
    ├── persistence/        # Сохранение/загрузка
    ├── localization/       # Система локализации
    ├── config/            # Управление конфигурацией
    │   └── config_manager.py
    └── mods/              # Поддержка модов
        └── mod_loader.py
```

## 🎯 Реализованные компоненты

### Domain Layer (Ядро системы)

#### Entities (Сущности)
- **Character** - основной класс персонажа с характеристиками, навыками, спасбросками
- **Race** - расы персонажей с бонусами к характеристикам
- **CharacterClass** - классы персонажей с способностями и мастерствами
- **Attribute** - характеристики (Strength, Dexterity, etc.)
- **Skill** - навыки с бонусами мастерства
- **SavingThrow** - спасброски с модификаторами

#### Value Objects (Объекты-значения)
- **Dice** - система бросков кубиков d4, d6, d8, d10, d12, d20
- **DiceResult** - результат броска с модификаторами и особыми результатами
- **RollModifierType** - типы модификаторов (Normal, Advantage, Disadvantage)

#### Services (Доменные сервисы)
- **CharacterGeneration** - генерация персонажей различными методами

#### Interfaces (Интерфейсы)
- **LocalizationInterface** - абстракция для системы локализации

### Application Layer (Бизнес-логика)

#### Use Cases (Сценарии использования)
- Планируется: CreateCharacter, LoadGame, SaveGame

#### DTO (Объекты передачи данных)
- Планируется: CharacterDTO, GameConfigDTO

### Interface Adapters Layer (Адаптеры)

#### Repositories (Репозитории)
- **CharacterRepository** - сохранение/загрузка персонажей в YAML

#### Gateways (Шлюзы)
- **LocalizationAdapter** - адаптер для существующей системы локализации

### Infrastructure Layer (Инфраструктура)

#### UI (Пользовательский интерфейс)
- **MainMenu** - главное меню игры
- **CharacterCreation** - пошаговое создание персонажа
- **CharacterMenu** - управление персонажем
- **Renderer** - консольный рендеринг
- **InputHandler** - обработка пользовательского ввода

#### Config (Конфигурация)
- **ConfigManager** - управление настройками игры

#### Mods (Модульность)
- **ModLoader** - загрузка пользовательских модов

## 📊 Данные и контент

```
data/
├── yaml/                   # YAML конфигурации
│   ├── attributes/         # Характеристики, классы, расы
│   │   ├── core_attributes.yaml
│   │   ├── races.yaml
│   │   ├── classes.yaml
│   │   ├── skills.yaml
│   │   └── saving_throws.yaml
│   ├── dice/              # Типы кубиков
│   │   └── core_dice.yaml
│   ├── items/             # Предметы
│   │   ├── weapons/
│   │   ├── armor/
│   │   └── potions/
│   ├── localization/      # Переводы
│   │   └── ru.yaml
│   └── monsters/          # Монстры
├── saves/                  # Сохранения персонажей
└── mods/                   # Пользовательские моды
    └── magic_mod/         # Пример мода
        ├── config.yaml
        ├── attributes/
        │   └── magic_power.yaml
        └── races/
            └── dragonborn.yaml
```

## 🎮 Игровые механики D&D 5e

### Система характеристик
- 6 основных характеристик: Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma
- Модификаторы: (value - 10) // 2
- Расовые бонусы к характеристикам
- Увеличение характеристик при повышении уровня

### Система навыков
- Навыки основаны на характеристиках
- Бонус мастерства: +2 (уровень 1-4), +3 (5-8), +4 (9-12), +5 (13-16), +6 (17-20)
- Экспертиза: двойной бонус мастерства

### Система кубиков
- d20 - для атак, проверок, спасбросков
- d4, d6, d8, d10, d12 - для урона
- Advantage/Disadvantage - бросок двух кубиков, выбор лучшего/худшего
- Критические успехи/неудачи при броске 1/20

### Система классов и рас
- Классы: Fighter, Wizard, Rogue, Cleric (базовый набор)
- Расы: Human, Elf, Dwarf, Halfling, Dragonborn (базовый набор)
- Уровни персонажей: 1-20 (планируется)

## 🛠️ Технологический стек

### Основные технологии
- **Python 3.13+** - основной язык разработки
- **PyYAML** - загрузка конфигураций и контента
- **Pathlib** - работа с файлами и путями
- **Dataclasses** - immutable объекты
- **Type Hints** - строгая типизация

### Инструменты разработки
- **pytest** - тестирование
- **black** - форматирование кода
- **ruff** - линтинг
- **mypy** - проверка типов

## 📋 Применяемые паттерны

### Creational Patterns
- **Factory Pattern** - создание персонажей, рас, классов
- **Builder Pattern** - пошаговое создание персонажей

### Structural Patterns  
- **Adapter Pattern** - адаптация системы локализации
- **Facade Pattern** - упрощенный интерфейс к системе кубиков

### Behavioral Patterns
- **Strategy Pattern** - различные методы бросков кубиков
- **Command Pattern** - система меню и команд

### Architectural Patterns
- **Repository Pattern** - абстракция над хранением данных
- **Dependency Injection** - внедрение зависимостей в Use Cases

## 🔄 Поток данных

### Создание персонажа
```
UI (CharacterCreation) 
  ↓ request
Use Case (CreateCharacter)
  ↓ domain objects
Domain Services (CharacterFactory)
  ↓ character
Repository (CharacterRepository)
  ↓ save
Infrastructure (YAML File)
```

### Загрузка персонажа
```
UI (CharacterMenu)
  ↓ request
Use Case (LoadCharacter)
  ↓ name
Repository (CharacterRepository)
  ↓ data
Infrastructure (YAML File)
  ↓ character
Domain (Character Entity)
  ↓ character
UI (Character Sheet)
```

## 🧪 Тестирование

### Текущие тесты
- **test_dice.py** - полные тесты системы кубиков (23 теста)
  - Базовые броски
  - Модификаторы (advantage/disadvantage)
  - Критические результаты
  - Валидация параметров
  - Фабричные методы
  - Интеграционные сценарии

### Планируемые тесты
- Тесты персонажей
- Тесты рас и классов
- Тесты Use Cases
- Тесты UI компонентов

## 🚀 Дальнейшее развитие

### Приоритет 1 (Core функционал)
1. **Use Cases** - реализация основных сценариев использования
2. **Repository** - полное сохранение/загрузка персонажей
3. **UI** - завершение интерфейса создания персонажа
4. **Тестирование** - покрытие основного функционала

### Приоритет 2 (Расширение)
1. **Combat System** - боевая система
2. **Inventory System** - инвентарь и предметы
3. **Level System** - повышение уровня и развитие
4. **Adventure System** - приключения и квесты

### Приоритет 3 (Модульность)
1. **Mod System** - полноценная система модов
2. **Plugin Architecture** - плагины для расширения
3. **Custom Content** - инструменты создания контента
4. **Multi-language** - полная локализация

## 📚 Документация

- **clean-architecture.md** - подробное описание Чистой Архитектуры
- **programming_principles.md** - принципы программирования SOLID
- **design_patterns.md** - паттерны проектирования в проекте
- **zen_python.md** - философия Python

Эта архитектура обеспечивает долгосрочную поддерживаемость, тестируемость и масштабируемость проекта DnD MUD в соответствии с современными практиками разработки.