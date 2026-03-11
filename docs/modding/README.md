# Руководство по созданию модов

## 🔧 Модификации D&D Text MUD

Это руководство поможет вам создавать моды для расширения игрового контента.

---

## 🎯 Что такое моды?

Моды - это YAML файлы, которые расширяют или изменяют игровой контент:
- Новые расы и классы
- Дополнительные предметы
- Новые приключения
- Изменение механик

---

## 📁 Структура модов

```
mods/
├── my-race-mod/
│   ├── mod.yaml          # Метаданные мода
│   ├── races.yaml        # Новые расы
│   └── abilities.yaml    # Дополнительные способности
├── adventure-mod/
│   ├── mod.yaml
│   └── adventures.yaml   # Новые приключения
└── total-conversion/
    ├── mod.yaml
    ├── races.yaml
    ├── classes.yaml
    ├── equipment.yaml
    └── adventures.yaml
```

---

## 📝 Создание простого мода

### Шаг 1: Создание директории мода
```bash
mkdir mods/my-first-mod
cd mods/my-first-mod
```

### Шаг 2: Файл метаданных (mod.yaml)
```yaml
name: "My First Mod"
version: "1.0.0"
author: "Your Name"
description: "Добавляет новую расу и класс"
game_version: "0.1.0"
dependencies: []
conflicts: []

# Приоритет загрузки (выше = позже применяются)
priority: 10

# Типы контента
content_types:
  - races
  - classes
  - equipment
```

### Шаг 3: Новая раса (races.yaml)
```yaml
# Расширение базовых рас
races:
  dragonborn:
    name: "Драконорожденный"
    description: "Потомки драконов с чешуйчатой кожей"
    ability_bonuses:
      strength: 2
      charisma: 1
    size: "medium"
    speed: 30
    age:
      min: 15
      max: 80
    languages: ["common", "draconic"]
    features:
      - name: "Драконья ancestry"
        description: "Вы получаете сопротивление одному типу урона"
        mechanics:
          type: "damage_resistance"
          choice: true
          options: ["fire", "cold", "lightning", "acid", "poison"]
    
    subraces:
      black_dragonborn:
        name: "Драконорожденный черного дракона"
        description: "Потомок черных драконов, повелителей кислоты"
        ability_bonuses: {}
        features:
          - name: "Сопротивление кислоте"
            description: "Вы получаете сопротивление урону кислотой"
            mechanics:
              type: "damage_resistance"
              damage_type: "acid"
```

### Шаг 4: Новый класс (classes.yaml)
```yaml
classes:
  sorcerer:
    name: "Чародей"
    description: "Врожденная магическая сила течет в ваших жилах"
    hit_dice: 6
    prime_abilities: ["charisma"]
    saving_throws: ["constitution", "charisma"]
    skill_choices: [
      "arcana", "deception", "insight", "intimidation",
      "persuasion", "religion"
    ]
    skill_choices_count: 2
    equipment:
      weapons: ["простые"]
      armor: ["нет"]
      tools: ["нет"]
    
    features:
      - id: "spellcasting"
        name: "Сотворение заклинаний"
        description: "Вы можете сотворять заклинания"
        level: 1
        feature_type: "passive"
        mechanics:
          type: "spellcasting"
          ability: "charisma"
          spell_slots:
            1: [4, 2]  # [каналы 1 уровня, каналы 2 уровня]
      
      - id: "sorcerous_origin"
        name: "Чародейское происхождение"
        description: "Выберите источник вашей силы"
        level: 1
        feature_type: "choice"
        mechanics:
          type: "subclass_choice"
          options: ["draconic_bloodline", "wild_magic"]
```

---

## 🎭 Создание приключений

### Структура приключения
```yaml
# adventures.yaml
adventures:
  tutorial_quest:
    name: "Начало пути"
    description: "Обучающее приключение для новичков"
    difficulty: "easy"
    estimated_time: "30 минут"
    level_range: [1, 2]
    
    # Начальная локация
    start_location: "village_square"
    
    # Локации
    locations:
      village_square:
        name: "Главная площадь деревни"
        description: "Небольшая деревенская площадь с колодцем посередине"
        exits:
          north: "village_shop"
          east: "tavern_entrance"
          south: "village_gate"
        npcs:
          - id: "village_elder"
            name: "Старейшина деревни"
            dialogue: "greeting"
        
      tavern_entrance:
        name: "Вход в таверну"
        description: "Шумный вход в таверну 'Рог изобилия'"
        exits:
          west: "village_square"
          inside: "tavern_main"
    
    # NPC и диалоги
    npcs:
      village_elder:
        name: "Старейшина деревни"
        description: "Пожилой мужчина с длинной бородой"
        dialogues:
          greeting:
            text: "Приветствую, путешественник! Мне нужна твоя помощь."
            choices:
              - text: "Чем я могу помочь?"
                next: "quest_offer"
              - text: "Я занят(а)."
                next: "farewell"
          
          quest_offer:
            text: "В нашем лесу поселились гоблины. Помоги нам избавиться от них."
            choices:
              - text: "Я помогу вам."
                action: "accept_quest"
                next: "quest_details"
              - text: "Сколько вы заплатите?"
                next: "quest_reward"
    
    # Квесты
    quests:
      goblin_problem:
        name: "Проблема с гоблинами"
        description: "Избавиться от гоблинов в лесу"
        giver: "village_elder"
        objectives:
          - type: "kill_enemies"
            target: "goblin"
            count: 5
            location: "forest_clearing"
        rewards:
          experience: 100
          gold: 50
          items: ["potion_healing"]
    
    # События
    events:
      goblin_encounter:
        type: "combat"
        location: "forest_clearing"
        enemies:
          - type: "goblin"
            count: 3
        victory:
          text: "Вы победили гоблинов!"
          rewards:
            experience: 25
            gold: 10
```

---

## ⚙️ Механики модов

### Типы механик
```yaml
# Типы механик в features
mechanics:
  # Бонус к характеристике
  ability_bonus:
    target: "strength"  # характеристика
    value: 2            # значение
  
  # Сопротивление урону
  damage_resistance:
    damage_type: "fire"  # тип урона
  
  # Навык
  skill_proficiency:
    skill: "stealth"      # навык
  
  # Язык
  language:
    language: "elvish"   # язык
  
  # Заклинание
  spell:
    spell: "fireball"    # заклинание
    uses_per_day: 3      # использований в день
  
  # Выбор
  choice:
    type: "skill_choice" # тип выбора
    count: 2             # количество
    options: ["stealth", "perception", "survival"]
```

### Условия и последствия
```yaml
# Условия
conditions:
  - type: "level"
    value: 3
  - type: "class"
    value: "fighter"
  - type: "race"
    value: "elf"

# Последствия
effects:
  - type: "grant_feature"
    feature: "second_wind"
  - type: "add_language"
    language: "dwarvish"
  - type: "modify_ability"
    ability: "constitution"
    modifier: 1
```

---

## 🔧 Продвинутые техники

### Наследование и модификация
```yaml
# Модификация существующей расы
races:
  human:
    # Переопределение описания
    description: "Люди - самая адаптивная раса"
    
    # Добавление новых особенностей
    features:
      - name: "Человеческая стойкость"
        description: "Вы получаете +1 к спасброскам от страха"
        mechanics:
          type: "save_bonus"
          condition: "fear"
          value: 1
```

### Условная логика
```yaml
# Условные особенности
features:
  - name: "Драконье дыхание"
    description: "Вы можете использовать дыхание дракона"
    mechanics:
      type: "special_action"
      uses_per_rest: 1
      conditions:
        - type: "subclass"
          value: "draconic_bloodline"
      effects:
        - type: "damage_area"
          damage_type: "fire"
          damage: "2d6"
          area: "cone_15ft"
```

### Интеграция с другими модами
```yaml
# mod.yaml
dependencies:
  - name: "base-game"
    version: ">=0.1.0"
  - name: "extra-races"
    version: "^1.0.0"

conflicts:
  - name: "another-race-mod"
    reason: "конфликт рас дварфов"
```

---

## 🧪 Тестирование модов

### Локальное тестирование
```bash
# Запуск игры с модом
dnd-mud --mod mods/my-first-mod

# Проверка синтаксиса YAML
python -c "import yaml; yaml.safe_load(open('mods/my-first-mod/races.yaml'))"
```

### Тестовый мод
```yaml
# test_mod.yaml
name: "Test Mod"
version: "0.1.0"
description: "Тестовый мод для проверки системы"

# Простая тестовая раса
races:
  test_race:
    name: "Тестовая раса"
    description: "Раса для тестирования"
    ability_bonuses:
      strength: 1
    size: "medium"
    speed: 30
    languages: ["common"]
```

---

## 📚 Примеры модов

### 1. Расовый мод
```yaml
# elven_subraces.yaml
races:
  elf:
    subraces:
      moon_elf:
        name: "Лунный эльф"
        description: "Эльфы с магическими способностями"
        ability_bonuses:
          intelligence: 1
        features:
          - name: "Лунная магия"
            description: "Вы знаете один заговор"
            mechanics:
              type: "cantrip_choice"
              count: 1
```

### 2. Предметный мод
```yaml
# magic_items.yaml
equipment:
  sword_of_flaming:
    name: "Пламенный меч"
    type: "weapon"
    category: "longsword"
    rarity: "rare"
    damage: "1d8 + 1"
    features:
      - name: "Пламенный удар"
        description: "Меч наносит дополнительный урон огнем"
        mechanics:
          type: "bonus_damage"
          damage_type: "fire"
          damage: "1d6"
```

### 3. Приключенческий мод
```yaml
# dark_forest.yaml
adventures:
  dark_forest:
    name: "Темный лес"
    description: "Мистическое приключение в проклятом лесу"
    difficulty: "medium"
    level_range: [3, 5]
    # ... остальная структура приключения
```

---

## 🚀 Публикация модов

### Подготовка к публикации
1. **Тестирование** - проверьте все механики
2. **Баланс** - убедитесь, что мод не нарушает баланс
3. **Документация** - создайте README для мода
4. **Версионирование** - используйте семантические версии

### Структура публикации
```
my-mod-release/
├── README.md              # Документация мода
├── mod.yaml              # Метаданные
├── content/              # YAML файлы контента
│   ├── races.yaml
│   ├── classes.yaml
│   └── ...
├── screenshots/          # Скриншоты (опционально)
└── examples/             # Примеры использования
```

---

## 🐛 Устранение проблем

### Частые ошибки
```yaml
# ❌ Неправильный синтаксис YAML
races:
  human
    name: "Человек"

# ✅ Правильный синтаксис
races:
  human:
    name: "Человек"
```

### Конфликты модов
- Используйте уникальные ID
- Проверяйте зависимости
- Тестируйте с другими модами

### Производительность
- Избегайте слишком больших файлов
- Используйте lazy loading
- Кэшируйте вычисления

---

## 📞 Сообщество моддеров

- **Discord** - сервер моддеров
- **GitHub** - репозитории модов
- **Wiki** - база знаний по моддингу

---

*Создавайте удивительные миры!*