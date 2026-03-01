# Руководство по созданию модов

## Обзор

Система модов позволяет расширять контент игры без изменения основного кода. Моды используют YAML формат для определения нового контента.

## Структура мода

```
Mods/my_awesome_mod/
├── mod_info.yaml          # Информация о моде
├── races.yaml            # Новые расы и подрасы
├── classes.yaml          # Новые классы и архетипы
├── backgrounds.yaml      # Новые предыстории
├── skills.yaml           # Новые навыки
├── languages.yaml        # Новые языки
├── spells.yaml           # Новые заклинания
├── items.yaml           # Новые предметы
├── adventures.yaml      # Новые приключения
├── npcs.yaml            # Новые NPC
├── factions.yaml        # Новые фракции
└── locale/              # Локализация мода
    ├── ru/
    │   └── mod.json
    └── en/
        └── mod.json
```

## Обязательные файлы

### mod_info.yaml

```yaml
name: "My Awesome Mod"
version: "1.0.0"
description: "Добавляет новые расы, классы и приключения"
author: "Modder Name"
email: "modder@example.com"
website: "https://github.com/modder/my-awesome-mod"
license: "MIT"
game_version: "0.1.0"
dependencies: []  # Список зависимых модов
conflicts: []     # Список конфликтующих модов
tags:
  - "races"
  - "classes"
  - "adventures"
```

## Создание контента

### 1. Новые расы (races.yaml)

```yaml
races:
  dragonborn:
    name: "Драконорожденный"
    description: "Гуманоид с драконьей чертами"
    size: "medium"
    speed: 30
    ability_bonuses:
      strength: 2
      charisma: 1
    traits:
      - name: "Драконья чешуя"
        description: "Броня +1 от неповреждаемой брони"
        type: "armor_bonus"
        value: 1
      - name: "Дыхательное оружие"
        description: "Раз в короткий отдых можете использовать дыхательное оружие"
        type: "special_action"
        damage_type: "fire"  # fire, cold, lightning, acid, poison
        damage: "2d10"
        dc: "8 + конституция + уровень"
    languages:
      - "Общий"
      - "Драконий"
    subraces:
      black_dragonborn:
        name: "Драконорожденный (черный дракон)"
        description: "Потомок черных драконов"
        damage_type: "acid"
        special_trait: "Устойчивость к кислоте"
      blue_dragonborn:
        name: "Драконорожденный (синий дракон)"
        description: "Потомок синих драконов"
        damage_type: "lightning"
        special_trait: "Устойчивость к молниям"
```

### 2. Новые классы (classes.yaml)

```yaml
classes:
  warlock:
    name: "Колдун"
    description: "Получил магическую силу от договора с потусторонней сущностью"
    hit_die: 8
    primary_ability: ["харизма"]
    saving_throws: ["мудрость", "харизма"]
    skill_choices: 2
    skill_options: ["дуговство", "история", "интровертация", "природа", "религия"]
    equipment:
      light_armor: true
      simple_weapons: true
      choices:
        - type: "weapon"
          options: ["simple_crossbow", "arcane_focus"]
        - type: "weapon"
          options: ["dagger", "dagger", "dagger"]
    features:
      level_1:
        - name: "Заклинания колдуна"
          description: "Вы можете колдовать заклинания"
          type: "spellcasting"
          spell_ability: "харизма"
          cantrips: 2
          spells_known:
            1: 1
        - name: "Другой мир"
          description: "Вы получаете благословение от вашего покровителя"
          type: "passive"
      level_2:
        - name: "Тайный магический круг"
          description: "Вы можете призвать своего покровителя"
          type: "action"
    subclasses:
      the_great_old_one:
        name: "Великий Древний"
        description: "Договор с древней, непостижимой сущностью"
        features:
          level_1:
            - name: "Пробуждение разума"
              description: "Вы можете общаться телепатически"
              type: "passive"
          level_6:
            - name: "Сущность-хранитель"
              description: "Ваш покровитель защищает вас"
              type: "reaction"
```

### 3. Новые предыстории (backgrounds.yaml)

```yaml
backgrounds:
  acolyte:
    name: "Послушник"
    description: "Вы служили в храме и изучали религиозные тексты"
    skill_proficiencies: ["дуговство", "религия"]
    tool_proficiencies: ["набор каллиграфа"]
    equipment:
      - "символ божества"
      - "молитвенник"
      - "5 палочек благовоний"
      - "одежда послушника"
      - "кошель с 15 зм"
    feature:
      name: "Убежище верующих"
      description: "Вы можете найти убежище в любом храме вашего божества"
    personality_traits:
      - "Я идеалист и верю в лучшее в людях"
      - "Я могу цитировать священные тексты часами"
      - "Я терпелив и слушаю других"
      - "Я верю, что все заслуживают второго шанса"
    ideals:
      - name: "Вера"
        description: "Я верю в свою веру и следую ей"
        alignment: "lawful good"
      - name: "Знание"
        description: "Знание - путь к просветлению"
        alignment: "neutral good"
    bonds:
      - "Я защищу свой храм любой ценой"
      - "Мой наставник научил меня всему, что я знаю"
      - "Я потерял семью, но нашел новую в храме"
    flaws:
      - "Я осуждаю тех, кто не разделяет мою веру"
      - "Я доверяю слишком легко"
      - "Я слепо следую приказам своих старших"
```

### 4. Новые навыки (skills.yaml)

```yaml
skills:
  survival:
    name: "Выживание"
    description: "Умение выживать в дикой природе"
    ability: "мудрость"
    description: "Вы можете находить пищу и воду, ориентироваться на местности, отслеживать существ"
  insight:
    name: "Проницательность"
    description: "Умение понимать намерения других"
    ability: "мудрость"
    description: "Вы можете определять истинные намерения существ, распознавать ложь"
  custom_skill:
    name: "Навык мода"
    description: "Пользовательский навык из мода"
    ability: "интеллект"
    description: "Описание нового навыка"
    special_rules:
      - "Особое правило 1"
      - "Особое правило 2"
```

### 5. Новые языки (languages.yaml)

```yaml
languages:
  draconic:
    name: "Драконий"
    type: "exotic"
    script: "draconic_script"
    speakers: ["драконы", "драконорожденные"]
    description: "Древний язык драконов, звучит гортанно и мощно"
  abyssal:
    name: "Бездонный"
    type: "exotic"
    script: "infernal_script"
    speakers: ["демоны", "дьяволы"]
    description: "Язык Нижних Плоскостей"
  custom_language:
    name: "Язык мода"
    type: "exotic"
    script: "custom_script"
    speakers: ["раса_мода"]
    description: "Описание языка из мода"
```

### 6. Новые заклинания (spells.yaml)

```yaml
spells:
  eldritch_blast:
    name: "Искажающий взрыв"
    level: 0
    school: "evocation"
    casting_time: "1 действие"
    range: "120 футов"
    components: ["V", "S"]
    duration: "мгновенно"
    description: "Создаёт луч энергии, который наносит 1d10 силового урона"
    damage:
      type: "force"
      dice: "1d10"
    classes: ["колдун"]
    higher_levels:
      - level: 5
        damage: "2d10"
      - level: 11
        damage: "3d10"
      - level: 17
        damage: "4d10"
  fireball:
    name: "Огненный шар"
    level: 3
    school: "evocation"
    casting_time: "1 действие"
    range: "150 футов"
    components: ["V", "S", "M"]
    material_component: "маленький шарик из летучей мыши и серы"
    duration: "мгновенно"
    description: "Создаёт взрыв огня в радиусе 20 футов"
    damage:
      type: "fire"
      dice: "8d6"
    save:
      type: "dexterity"
      dc: "8 + уровень модификатор способностей + бонус мастерства"
      half_damage: true
    classes: ["волшебник", "колдун", "sorcerer"]
  custom_spell:
    name: "Заклинание мода"
    level: 1
    school: "custom_school"
    casting_time: "1 действие"
    range: "касание"
    components: ["V", "S"]
    duration: "1 минута"
    description: "Описание заклинания из мода"
    effects:
      - type: "healing"
        amount: "2d4 + 1"
      - type: "buff"
        stat: "strength"
        bonus: 2
    classes: ["custom_class"]
```

### 7. Новые предметы (items.yaml)

```yaml
items:
  longsword:
    name: "Длинный меч"
    type: "weapon"
    category: "martial_melee"
    damage: "1d8 рубящий"
    weight: 3
    cost: "15 зм"
    properties: ["versatile (1d10)"]
    description: "Классический меч воина"
  magic_sword:
    name: "Магический меч +1"
    type: "weapon"
    category: "martial_melee"
    damage: "1d8 рубящий"
    weight: 3
    cost: "1000 зм"
    properties: ["versatile (1d10)", "magic", "+1"]
    description: "Магический меч, который даёт +1 к атакам и урону"
    rarity: "rare"
    requirements:
      level: 5
  custom_item:
    name: "Предмет мода"
    type: "custom_type"
    category: "custom_category"
    weight: 1
    cost: "50 зм"
    description: "Описание предмета из мода"
    effects:
      - type: "passive"
        description: "Эффект 1"
      - type: "active"
        description: "Эффект 2"
        uses_per_day: 3
```

### 8. Новые приключения (adventures.yaml)

```yaml
adventures:
  custom_adventure:
    name: "Приключение из мода"
    description: "Описание приключения"
    difficulty: "medium"
    recommended_level: [3, 5]
    estimated_time: "4-6 часов"
    tags: ["combat", "exploration", "social"]
    chapters:
      chapter_1:
        name: "Глава 1: Начало"
        description: "Начало приключения"
        scenes:
          scene_1:
            name: "Сцена 1: Встреча"
            type: "dialogue"
            location: "tavern"
            npc: "tavern_keeper"
            dialogue:
              - speaker: "tavern_keeper"
                text: "Добро пожаловать, странник!"
                responses:
                  - text: "Я ищу работу"
                    next_scene: "scene_2"
                  - text: "Расскажи новости"
                    next_scene: "scene_3"
          scene_2:
            name: "Сцена 2: Задание"
            type: "quest"
            description: "Тавернщик предлагает задание"
            quest:
              name: "Очистить пещеру"
              description: "В пещере поселились гоблины"
              objectives:
                - type: "kill"
                  target: "goblins"
                  count: 5
                - type: "collect"
                  target: "goblin_treasure"
                  count: 1
              rewards:
                xp: 200
                gold: 100
                items: ["health_potion"]
      chapter_2:
        name: "Глава 2: Пещера"
        description: "Исследование пещеры"
        encounters:
          - type: "combat"
            enemies: ["goblin", "goblin", "goblin_shaman"]
            location: "cave_entrance"
          - type: "skill_check"
            skill: "perception"
            dc: 15
            success: "Находите тайник"
            failure: "Проходите мимо"
```

## Локализация мода

### locale/ru/mod.json

```json
{
  "races.dragonborn.name": "Драконорожденный",
  "races.dragonborn.description": "Гуманоид с драконьей чертами",
  "classes.warlock.name": "Колдун",
  "classes.warlock.description": "Получил магическую силу от договора",
  "spells.eldritch_blast.name": "Искажающий взрыв",
  "spells.eldritch_blast.description": "Создаёт луч энергии",
  "items.magic_sword.name": "Магический меч +1",
  "items.magic_sword.description": "Магический меч с бонусом +1",
  "adventures.custom_adventure.name": "Приключение из мода",
  "adventures.custom_adventure.description": "Описание приключения"
}
```

### locale/en/mod.json

```json
{
  "races.dragonborn.name": "Dragonborn",
  "races.dragonborn.description": "Humanoid with draconic features",
  "classes.warlock.name": "Warlock",
  "classes.warlock.description": "Gained magical power through a pact",
  "spells.eldritch_blast.name": "Eldritch Blast",
  "spells.eldritch_blast.description": "Creates a beam of energy",
  "items.magic_sword.name": "Magic Sword +1",
  "items.magic_sword.description": "Magical sword with +1 bonus",
  "adventures.custom_adventure.name": "Custom Adventure",
  "adventures.custom_adventure.description": "Adventure description"
}
```

## Валидация модов

### Правила валидации

1. **Обязательные поля**: Все обязательные поля должны быть заполнены
2. **Типы данных**: Правильные типы данных для каждого поля
3. **Ссылки**: Все ссылки на другие объекты должны существовать
4. **Баланс**: Проверка баланса характеристик и способностей
5. **Совместимость**: Проверка совместимости с версией игры

### Тестирование мода

```bash
# Проверка валидации
python -m dnd_mud.mods.validator --mod-path Mods/my_mod

# Тест загрузки мода
python -m dnd_mud.mods.loader --test-mod my_mod

# Проверка конфликтов
python -m dnd_mud.mods.manager --check-conflicts my_mod
```

## Распространение модов

### Пакетирование

```bash
# Создание пакета мода
python -m dnd_mud.mods.packager --mod my_mod --output my_mod.zip

# Установка мода
python -m dnd_mud.mods.installer --install my_mod.zip

# Удаление мода
python -m dnd_mud.mods.manager --uninstall my_mod
```

### Публикация

1. Упакуйте мод в ZIP архив
2. Загрузите на GitHub Releases или мод-хаб
3. Создайте README.md с описанием
4. Добавьте скриншоты и видео
5. Укажите зависимости и совместимость

## Лучшие практики

### 1. Структура
- Используйте понятные имена файлов
- Группируйте связанный контент
- Следуйте соглашениям об именовании

### 2. Баланс
- Тестируйте новый контент
- Избегайте слишком сильных предметов
- Сохраняйте баланс с оригинальным контентом

### 3. Совместимость
- Указывайте зависимости
- Проверяйте конфликты
- Тестируйте с другими модами

### 4. Локализация
- Предоставляйте переводы
- Используйте ключи для всех строк
- Тестируйте разные языки

### 5. Документация
- Описывайте новый контент
- Добавляйте примеры использования
- Объясняйте механику

## Пример простого мода

```
Mods/simple_race_mod/
├── mod_info.yaml
├── races.yaml
└── locale/
    ├── ru/
    │   └── mod.json
    └── en/
        └── mod.json
```

**mod_info.yaml**:
```yaml
name: "Simple Race Mod"
version: "1.0.0"
description: "Добавляет новую расу"
author: "Modder"
game_version: "0.1.0"
```

**races.yaml**:
```yaml
races:
  catfolk:
    name: "Кошколюд"
    description: "Гуманоид с кошачьими чертами"
    size: "medium"
    speed: 30
    ability_bonuses:
      dexterity: 2
      charisma: 1
    traits:
      - name: "Кошачье равновесие"
        description: "Преимущество на проверки равновесия"
    languages:
      - "Общий"
      - "Кошачий"
```

Этот пример показывает минимальный мод, добавляющий одну новую расу в игру.
