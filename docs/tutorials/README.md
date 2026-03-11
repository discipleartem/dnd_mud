# Обучающие материалы

## 📚 Туториалы и гайды по D&D Text MUD

Пошаговые инструкции, примеры кода и лучшие практики для игроков и разработчиков.

---

## 📋 Содержание

- [Для игроков](#для-игроков)
- [Для разработчиков](#для-разработчиков)
- [Для моддеров](#для-моддеров)
- [Частые вопросы](#частые-вопросы)
- [Лучшие практики](#лучшие-практики)

---

## 👨‍💼 Для игроков

### Туториал 1: Быстрый старт для новичков

#### Шаг 1: Установка и запуск
```bash
# Клонирование и установка
git clone https://github.com/discipleartem/dnd_mud.git
cd dnd_mud
python -m venv .venv
source .venv/bin/activate
pip install -e .

# Запуск игры
dnd-mud
```

#### Шаг 2: Создание первого персонажа
1. Выберите "Создание персонажа" в главном меню
2. Введите имя (например, "Арториус")
3. Выберите расу "Человек" для простоты
4. Выберите класс "Воин" - отличный выбор для новичков
5. Используйте стандартные характеристики [15, 14, 13, 12, 10, 8]
6. Распределите: Сила 15, Ловкость 14, Телосложение 13, остальные по порядку
7. Выберите предысторию "Воин"
8. Выберите навыки "Атлетика" и "Запугивание"
9. Сохраните персонажа

#### Шаг 3: Основные команды
```bash
# В игре:
/status      # посмотреть характеристики
/inventory   # посмотреть инвентарь
/help        # список всех команд
/look        # осмотреться
```

### Туториал 2: Первый бой

#### Подготовка к бою
```python
# Пример подготовки к бою
def prepare_for_combat():
    # 1. Проверка оружия
    if not hero.weapon:
        equip_default_weapon()
    
    # 2. Проверка брони
    if not hero.armor:
        equip_default_armor()
    
    # 3. Проверка здоровья
    if hero.hp < hero.max_hp:
        use_potion_if_available()
```

#### Тактика боя
1. **Оценка противника** - используйте `/look` для изучения врага
2. **Выбор позиции** - начните с атаки если у вас преимущество
3. **Использование способностей** - не забывайте про классовые умения
4. **Лечение** - используйте зелья между боями

#### Пример хода в бою
```bash
# Ваш ход:
/attack goblin    # атаковать гоблина
/cast healing_word ally  # вылечить союзника (если бард/жрец)
/defend           # защитная стойка
```

### Туториал 3: Исследование мира

#### Навигация
```bash
# Команды перемещения:
/go north         # идти на север
/enter tavern     # войти в таверну
/exit             # выйти из здания
```

#### Взаимодействие с NPC
```bash
# Диалоги:
/talk elder       # поговорить со старейшиной
/ask quest        # спросить о квестах
/greet            # поздороваться
```

#### Поиск сокровищ
```bash
# Поиск:
/search room      # обыскать комнату
/open chest       # открыть сундук
/take item        # взять предмет
```

---

## 👨‍💻 Для разработчиков

### Туториал 1: Добавление новой расы

#### Шаг 1: Создание YAML файла
```yaml
# data/custom_races.yaml
races:
  tiefling:
    name: "Тифлинг"
    description: "Потомки демонов с ада"
    ability_bonuses:
      charisma: 2
      intelligence: 1
    size: "medium"
    speed: 30
    age:
      min: 18
      max: 100
    languages: ["common", "infernal"]
    features:
      - name: "Адастское сопротивление"
        description: "Вы получаете сопротивление урону огнем"
        mechanics:
          type: "damage_resistance"
          damage_type: "fire"
      - name: "Адастская магия"
        description: "Вы знаете заклинание thaumaturgy"
        mechanics:
          type: "innate_spell"
          spell: "thaumaturgy"
          uses_per_day: 3
```

#### Шаг 2: Создание сущности
```python
# src/entities/race.py
class Race:
    def __init__(self, race_id: str, data: dict):
        self.id = race_id
        self.name = data["name"]
        self.description = data["description"]
        self.ability_bonuses = data["ability_bonuses"]
        self.size = data["size"]
        self.speed = data["speed"]
        self.languages = data["languages"]
        self.features = [Feature(f) for f in data["features"]]
    
    def apply_bonuses(self, character: "Character") -> None:
        """Применить расовые бонусы к персонажу"""
        for ability, bonus in self.ability_bonuses.items():
            character.abilities[ability] += bonus
        
        # Применить особенности
        for feature in self.features:
            character.add_feature(feature)
```

#### Шаг 3: Тестирование
```python
# tests/test_tiefling_race.py
def test_tiefling_creation():
    """Тест создания тифлинга"""
    race_data = load_race_data("tiefling")
    tiefling = Race("tiefling", race_data)
    
    character = Character.create_new()
    tiefling.apply_bonuses(character)
    
    assert character.abilities["charisma"] == 12  # 10 + 2
    assert character.abilities["intelligence"] == 11  # 10 + 1
    assert "fire" in character.damage_resistances
```

### Туториал 2: Создание нового заклинания

#### Шаг 1: Определение заклинания
```yaml
# data/spells.yaml
spells:
  fire_bolt:
    name: "Огненный снаряд"
    level: 0
    school: "evocation"
    casting_time: "1 действие"
    range: "120 футов"
    components: ["V", "S"]
    duration: "мгновенная"
    description: "Вы создаете три огненных снаряда"
    requires_attack_roll: true
    damage_type: "fire"
    damage_dice: "2d10"
    save_type: null
```

#### Шаг 2: Реализация механики
```python
# src/entities/spell.py
class Spell:
    def cast(self, caster: Character, target: Character) -> SpellResult:
        """Применение заклинания"""
        result = SpellResult()
        
        if self.requires_attack_roll:
            attack_roll = d20() + caster.spell_attack_bonus
            result.attack_roll = attack_roll
            
            if attack_roll >= target.armor_class:
                # Попадание!
                damage = roll_dice(self.damage_dice)
                damage += caster.spell_damage_modifier
                
                # Применение сопротивлений
                if target.has_resistance(self.damage_type):
                    damage = damage // 2
                
                target.take_damage(damage)
                result.damage = damage
                result.hit = True
            else:
                result.hit = False
        
        return result
```

### Туториал 3: Создание UI компонента

#### Шаг 1: Базовый класс UI
```python
# src/console/ui_component.py
from abc import ABC, abstractmethod

class UIComponent(ABC):
    def __init__(self, renderer: "UIRenderer"):
        self.renderer = renderer
    
    @abstractmethod
    def render(self) -> None:
        """Отрисовка компонента"""
        pass
    
    @abstractmethod
    def handle_input(self, key: str) -> bool:
        """Обработка ввода"""
        pass
```

#### Шаг 2: Комент персонажа
```python
# src/console/character_sheet.py
class CharacterSheet(UIComponent):
    def __init__(self, renderer: "UIRenderer", character: Character):
        super().__init__(renderer)
        self.character = character
        self.current_page = 0
    
    def render(self) -> None:
        """Отрисовка карточки персонажа"""
        self.renderer.clear_screen()
        self.renderer.show_title(f"Карточка персонажа: {self.character.name}")
        
        if self.current_page == 0:
            self._render_basic_info()
        elif self.current_page == 1:
            self._render_combat_info()
        elif self.current_page == 2:
            self._render_skills()
        
        self.renderer.show_navigation(["[1] Базовая", "[2] Бой", "[3] Навыки", "[ESC] Выход"])
    
    def _render_basic_info(self) -> None:
        """Отрисовка базовой информации"""
        info = [
            f"Уровень: {self.character.level}",
            f"Раса: {self.character.race.name}",
            f"Класс: {self.character.class.name}",
            "",
            "Характеристики:",
        ]
        
        for ability, score in self.character.abilities.items():
            mod = get_ability_modifier(score)
            info.append(f"  {ability}: {score} ({mod:+d})")
        
        self.renderer.show_info(info)
    
    def handle_input(self, key: str) -> bool:
        """Обработка ввода"""
        if key == "1":
            self.current_page = 0
            return True
        elif key == "2":
            self.current_page = 1
            return True
        elif key == "3":
            self.current_page = 2
            return True
        elif key == "ESC":
            return False
        
        return True
```

---

## 🔧 Для моддеров

### Туториал 1: Создание простого мода

#### Шаг 1: Структура мода
```
my_first_mod/
├── mod.yaml
├── races.yaml
├── classes.yaml
└── README.md
```

#### Шаг 2: Метаданные мода
```yaml
# mod.yaml
name: "My First Mod"
version: "1.0.0"
author: "YourName"
description: "Добавляет новую расу и класс"
game_version: "0.1.0"
dependencies: []
priority: 10
content_types:
  - races
  - classes
```

#### Шаг 3: Новое содержание
```yaml
# races.yaml
races:
  dragonborn:
    name: "Драконорожденный"
    description: "Потомки драконов"
    ability_bonuses:
      strength: 2
      charisma: 1
    size: "medium"
    speed: 30
    languages: ["common", "draconic"]
    features:
      - name: "Дыхание дракона"
        description: "Вы можете использовать дыхание дракона"
        mechanics:
          type: "special_action"
          uses_per_rest: 1
          damage_type: "choice"  # fire, cold, lightning, acid, poison
          damage_dice: "2d6"
          area: "cone_15ft"
```

### Туториал 2: Создание приключения

#### Шаг 1: Структура приключения
```yaml
# adventures.yaml
adventures:
  the_lost_tomb:
    name: "Затерянная гробница"
    description: "Исследуйте древнюю гробницу и найдите сокровища"
    difficulty: "medium"
    level_range: [3, 5]
    estimated_time: "2-3 часа"
    
    start_location: "entrance"
    
    locations:
      entrance:
        name: "Вход в гробницу"
        description: "Каменная лестница ведет вниз во тьму"
        exits:
          down: "main_chamber"
          outside: "surface"
        encounters:
          - type: "trap"
            trigger: "first_entry"
            effect: "fall_damage_1d6"
      
      main_chamber:
        name: "Главный зал"
        description: "Большой зал с древними саркофагами"
        exits:
          north: "treasure_room"
          east: "puzzle_room"
          west: "monster_lair"
          up: "entrance"
        npcs:
          - id: "guardian_spirit"
            name: "Дух-хранитель"
            dialogue: "greeting"
    
    dialogues:
      guardian_spirit:
        greeting:
          text: "Кто смеет тревожить покой усопших?"
          choices:
            - text: "Я искатель приключений."
              next: "adventurer_response"
            - text: "Я пришел за сокровищами."
              next: "treasure_seeker_response"
            - text: "Просто исследую."
              next: "explorer_response"
        
        adventurer_response:
          text: "Тогда докажи свою доблесть! Реши загадку или сразись с чудовищем."
          choices:
            - text: "Я готов к испытанию."
                action: "start_challenge"
                next: "challenge_accepted"
            - text: "Я лучше уйду."
                next: "leave_in_peace"
    
    encounters:
      crypt_guardian:
        type: "combat"
        enemies:
          - type: "skeleton"
            count: 2
          - type: "specter"
            count: 1
        victory:
          text: "Вы победили стражей гробницы!"
          rewards:
            experience: 150
            items: ["potion_healing", "scroll_magic_missile"]
        defeat:
          text: "Вы были побеждены..."
          consequences:
            - type: "wake_up_entrance"
              message: "Вы очнулись у входа, раненые, но живые."
    
    puzzles:
      rune_puzzle:
        type: "sequence"
        description: "Расположите руны в правильном порядке"
        solution: ["fire", "water", "earth", "air"]
        hints:
          - "Огонь сжигает, вода тушит"
          - "Земля тяжелая, воздух легкий"
        success:
          text: "Дверь открылась!"
          reward: "access_to_treasure_room"
        failure:
          text: "Ничего не произошло. Попробуйте еще раз."
          penalty: "minor_electric_damage"
```

---

## ❓ Частые вопросы

### Для игроков

**Q: Как восстановить здоровье?**
A: Используйте зелья лечения, сделайте короткий отдых (восстанавливает 1/2 здоровья) или длинный отдых (полное восстановление).

**Q: Что делать если застрял в квесте?**
A: Используйте команду `/quest` для подсказок, `/talk` с NPC для информации, или `/help` для списка команд.

**Q: Как изменить управление?**
A: Настройки управления находятся в главном меню → Настройки → Управление.

**Q: Можно ли переименовать персонажа?**
A: Нет, имя персонажа нельзя изменить после создания. Создайте нового персонажа.

### Для разработчиков

**Q: Как добавить новую характеристику?**
A: Измените сущность Character и обновите все связанные системы (расы, классы, предметы).

**Q: Как протестировать боевые механики?**
A: Используйте модуль `tests/test_combat.py` и создавайте тестовые сценарии.

**Q: Где хранятся сохранения?**
A: В директории `saves/` в формате JSON. Каждый персонаж в отдельном файле.

**Q: Как добавить новую команду?**
A: Создайте новый класс в `src/console/commands/` и зарегистрируйте его в `CommandHandler`.

### Для моддеров

**Q: Мой мод не загружается, что делать?**
A: Проверьте синтаксис YAML файлов, убедитесь что `mod.yaml` заполнен корректно, проверьте зависимости.

**Q: Как сделать мод совместимым с другими модами?**
A: Используйте уникальные ID для всего контента, проверяйте конфликты имен, тестируйте с популярными модами.

**Q: Как добавить новую механику в моде?**
A: Используйте поле `mechanics` в особенностях и определите обработку в коде мода или через API.

---

## 💡 Лучшие практики

### Для игроков

#### Создание персонажа
1. **Планируйте развитие** - думайте о том, каким персонаж будет на высоких уровнях
2. **Синергия расы и класса** - выбирайте комбинации, которые дополняют друг друга
3. **Баланс характеристик** - не игнорируйте важные для класса характеристики
4. **Ролевая игра** - создайте интересную предысторию для лучшего погружения

#### Тактика боя
1. **Используйте окружение** - укрывайтесь за препятствиями, используйте высоту
2. **Управляйте ресурсами** - экономьте слоты заклинаний, способности на решающие моменты
3. **Командная работа** - координируйте действия с союзниками
4. **Адаптируйтесь** - меняйте тактику в зависимости от противника

#### Исследование
1. **Тщательно обыскивайте** - проверяйте все углы и контейнеры
2. **Общайтесь с NPC** - многие подсказки скрыты в диалогах
3. **Записывайте важное** - ведите заметки о квестах и локациях
4. **Экспериментируйте** - пробуйте разные решения задач

### Для разработчиков

#### Написание кода
1. **SOLID принципы** - каждый класс должен иметь одну ответственность
2. **Type hints** - используйте типы везде для лучшей читаемости
3. **Тестирование** - пишите тесты для каждой новой функции
4. **Документация** - комментируйте сложные места и API

#### Архитектура
1. **Разделение слоев** - не смешивайте логику с UI
2. **Интерфейсы** - используйте абстракции для легкой замены реализаций
3. **Конфигурация** - выносите настраиваемые параметры в конфигурационные файлы
4. **Масштабируемость** - думайте о будущем расширении проекта

#### Производительность
1. **Ленивая загрузка** - загружайте данные только когда нужно
2. **Кэширование** - кэшируйте часто используемые вычисления
3. **Асинхронность** - используйте async для долгих операций
4. **Профилирование** - измеряйте производительность перед оптимизацией

### Для моддеров

#### Создание контента
1. **Баланс** - проверяйте что новый контент не нарушает баланс игры
2. **Совместимость** - тестируйте с другими популярными модами
3. **Качество** - проверяйте орфографию и грамматику в текстах
4. **Документация** - создайте README с описанием вашего мода

#### Технические аспекты
1. **Версионирование** - используйте семантические версии
2. **Зависимости** - четко указывайте зависимости и версии игры
3. **Тестирование** - создавайте тестовые сценарии для вашего контента
4. **Обратная связь** - слушайте отзывы игроков и улучшайте мод

---

## 📚 Дополнительные ресурсы

### Официальные ресурсы
- [D&D 5e Player's Handbook](https://dnd.wizards.com/products/tabletop-games/rpg-products/rpg_playershandbook)
- [System Reference Document (SRD)](https://www.dndbeyond.com/sources/srd)
- [Open5E](https://open5e.com/) - открытая лицензия D&D 5e

### Сообщество
- [Reddit r/DnD](https://reddit.com/r/DnD)
- [Discord D&D](https://discord.gg/dnd)
- [GitHub D&D Text MUD](https://github.com/discipleartem/dnd_mud)

### Инструменты
- [YAML Linter](https://yaml-online-parser.appspot.com/) - проверка YAML
- [Dice Roller](https://roll20.net/) - онлайн броски кубиков
- [Character Builder](https://dndbeyond.com/) - конструктор персонажей

---

*Создавайте, исследуйте и наслаждайтесь миром D&D Text MUD!*