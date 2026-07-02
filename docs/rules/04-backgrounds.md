---
phb_chapter: 4
phb_section: Личность и предыстория
phb_pages:
- 121
- 142
phb_part: 1
id: 04-backgrounds
tags:
- chapter
mud_status: partial
---

# Личность и предыстория

> Источник: PHB, стр. 121–142. Пересказ правил, не дословная копия PHB.

## Детальные карточки

| ID | Название | Файл | Статус MUD |
|----|----------|------|------------|
| `acolyte` | Прислужник | [acolyte.md](backgrounds/acolyte.md) | partial |
| `charlatan` | Шарлатан | [charlatan.md](backgrounds/charlatan.md) | partial |
| `criminal` | Преступник | [criminal.md](backgrounds/criminal.md) | partial |
| `entertainer` | Артист | [entertainer.md](backgrounds/entertainer.md) | partial |
| `folk_hero` | Народный герой | [folk_hero.md](backgrounds/folk_hero.md) | partial |
| `guild_artisan` | Гильдейский ремесленник | [guild_artisan.md](backgrounds/guild_artisan.md) | partial |
| `hermit` | Отшельник | [hermit.md](backgrounds/hermit.md) | partial |
| `noble` | Благородный | [noble.md](backgrounds/noble.md) | partial |
| `outlander` | Чужеземец | [outlander.md](backgrounds/outlander.md) | partial |
| `sage` | Мудрец | [sage.md](backgrounds/sage.md) | partial |
| `sailor` | Моряк | [sailor.md](backgrounds/sailor.md) | partial |
| `soldier` | Солдат | [soldier.md](backgrounds/soldier.md) | partial |
| `urchin` | Беспризорник | [urchin.md](backgrounds/urchin.md) | partial |

## Для игроков

- ЕРСОНАЖИ ХАРАКТЕРИЗУЮТСЯ НЕ
- только расой и классом. Они — личности, с собственной историей, связями и возможностями, выходящими за определения классов и рас. Эта глава описывает детали, отличающие персонажей друг от друга, включая такие основы, как имя и физическое описание, правила предысторий и языков, личностные особенности и мировоззрение.
- ОПИСАНИЕ ПЕРСОНАЖА Имя вашего персонажа и его физическое описание могут быть первым, что другие игроки узнают о вас. Поэтому стоит подумать, как эти показатели будут отражать характер вашего персонажа, которого вы уже придумали в своей голове.
- ИМЯ Описание расы вашего персонажа включает примеры имён для представителей этой расы. Вложите некоторый смысл в своё имя, даже если вы просто выбираете его из списка.
- ПОЛ Вы можете играть мужчиной или женщиной, не получая особых преимуществ или недостатков. Подумайте о том, как ваш персонаж относится к вопросу полов. Например, мужчина жрец дроу может отрицать традиционное разделение по половому признаку общества своей расы, и именно поэтому он покинул его и отправился на поверхность.
- ТИКА И АРТЕМИС: КОНТРАСТНЫЕ ПЕРСОНАЖИ Информация из этой главы делает персонажей непохожими друг на друга.
- Давайте рассмотрим двух людей воинов.
- Тика Вейлан родом из мира Саги о Копье.
- РОСТ И ВЕС Вы можете определить рост и вес своего персонажа, используя информацию, приведённую в описании вашей расы, или же воспользовавшись приведённой ниже таблицей.
- Подумайте, как характеристики вашего персонажа могут повлиять на его рост и вес.
- Слабый, но подвижный персонаж может быть худым, в то время как сильный и стойкий персонаж может быть высоким или просто крупным.
- СЛУЧАЙНЫЙ РОСТ И ВЕС Базовый Мод. рост Раса роста Человек 4'8'' +2к10 Дварф, горный 4' +2к4 Дварф, холмовой 3'8'' +2к4 Эльф, высший 4'6'' +2к10 Эльф, лесной 4'6'' +2к10 Эльф, дроу 4'5'' +2к6 Полурослик 2'7'' +2к4 Драконорождённый 5'6'' +2к8 Гном 2'11'' +2к4 Полуэльф 4'9'' +2к8 Полуорк 4'10'' +2к10 Тифлинг 4'9'' +2к8

## Для разработчиков

| Аспект | Значение |
|--------|----------|
| Статус | **Частично** — выбор предыстории, навыки, языки, **стартовое снаряжение в инвентаре**; personality/inspiration/feature runtime — Phase 2 |
| YAML | [`database/backgrounds/backgrounds.yaml`](../../database/backgrounds/backgrounds.yaml) |
| Core | [`core/backgrounds.py`](../../core/backgrounds.py) |
| UI | [`ui/menus/backgrounds.py`](../../ui/menus/backgrounds.py) |
| Flow | После **характеристик**, до **класса**; языки — отдельный шаг после предыстории |

### YAML-схема

Канон: [`docs/DATA_SCHEMA.md`](../DATA_SCHEMA.md). Механика — только в `grants[]`.

```yaml
backgrounds:
  acolyte:
    name: { ru: "...", en: "..." }
    description: { ru: "...", en: "..." }
    grants:
      - type: skill_proficiency
        skills: [insight, religion]
      - type: language
        count: 2
        choice: true
        pool: common
      - type: equipment_item
        items:
          - { kind: equipment, id: emblem, qty: 1 }
    inventory_tool_pools:   # опционально: picks → инвентарь PHB
      - musical_instruments
    equipment: { ru: [...], en: [...] }   # flavor для UI; предметы — в equipment_item
    feature:   # flavor; не game engine
      name: { ru: "...", en: "..." }
      description: { ru: "...", en: "..." }
```

- `language` grant, поле `pool`: `common` (по умолчанию), `exotic` или `any` — см. [`database/core/languages.yaml`](../../database/core/languages.yaml).
- **Экзотические языки** доступны для выбора только при `pool: exotic` / `pool: any`.

### Модель и сохранение

- `Character.background_id` в JSON сейва.
- Навыки предыстории входят в `Character.skills` с источником `background` при выборе классовых навыков.
- Стартовое снаряжение: grant `equipment_item` + picks из `inventory_tool_pools` → `core/backgrounds.get_background_equipment_items`, merge в `save_character`.

### Не реализовано

- Таблицы personality (черты, идеалы, привязанности, изъяны) и Inspiration.
- Механика background feature в engine.



