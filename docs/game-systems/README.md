# Игровые системы

## ⚔️ Механики D&D Text MUD

Подробное описание игровых систем и механик, реализованных в игре.

---

## 📋 Содержание

- [Боевая система](#боевая-система)
- [Система уровней и прокачки](#система-уровней-и-прокачки)
- [Торговая система](#торговая-система)
- [Система репутации](#система-репутации)
- [Система заклинаний](#система-заклинаний)
- [Инвентарь и предметы](#инвентарь-и-предметы)

---

## ⚔️ Боевая система

### Обзор
Боевая система реализует пошаговые бои Dungeons & Dragons 5e с адаптацией для консольного формата.

### Фазы боя
1. **Инициатива** - определение порядка хода
2. **Ход персонажа** - действие в свой ход
3. **Ход противника** - реакция NPC
4. **Проверка условий** - окончание боя

### Инициатива
```python
def roll_initiative(character: Character) -> int:
    """Бросок инициативы"""
    return d20() + character.dexterity_modifier

# Пример:
# d20() = 15, DEX модификатор = +2
# Инициатива = 17
```

### Действия в бою

#### Атака (Attack)
```python
def attack(attacker: Character, target: Character, weapon: Weapon) -> AttackResult:
    """Выполнение атаки"""
    # Бросок атаки
    attack_roll = d20() + attacker.get_attack_bonus(weapon)
    
    # Проверка попадания
    if attack_roll >= target.armor_class:
        # Попадание!
        damage = weapon.roll_damage() + attacker.get_damage_bonus(weapon)
        target.take_damage(damage)
        return AttackResult(hit=True, damage=damage)
    else:
        # Промах
        return AttackResult(hit=False, damage=0)
```

#### Защита (Defend)
```python
def defend(character: Character) -> DefenseResult:
    """Защитная стойка"""
    # Преимущество на следующий бросок спасброска
    character.add_temporary_effect("defensive_stance", duration=1)
    return DefenseResult(ac_bonus=2, advantage_on_save=True)
```

#### Заклинание (Spell)
```python
def cast_spell(caster: Character, spell: Spell, target: Character) -> SpellResult:
    """Применение заклинания"""
    # Проверка слотов
    if not caster.has_spell_slot(spell.level):
        raise NoSpellSlotsError()
    
    # Бросок атаки заклинания
    if spell.requires_attack_roll:
        attack_roll = d20() + caster.spell_attack_bonus
        if attack_roll >= target.spell_save_dc:
            # Попадание заклинанием
            damage = spell.roll_damage()
            target.take_damage(damage)
            return SpellResult(success=True, damage=damage)
    else:
        # Спасбросок цели
        save_roll = d20() + target.get_save_modifier(spell.save_type)
        if save_roll < spell.save_dc:
            # Провал спасброска
            spell.apply_effect(target)
            return SpellResult(success=True, effect=spell.effect)
    
    return SpellResult(success=False)
```

### Статусы и эффекты
```python
class StatusEffect:
    def __init__(self, name: str, duration: int, effects: dict):
        self.name = name
        self.duration = duration
        self.effects = effects
    
    def apply(self, character: Character) -> None:
        """Применить эффект к персонажу"""
        for effect_type, value in self.effects.items():
            if effect_type == "disadvantage_attacks":
                character.add_disadvantage("attack")
            elif effect_type == "damage_resistance":
                character.add_resistance(value)
```

---

## 📈 Система уровней и прокачки

### Опыт и уровни
```python
# Таблица опыта (до 10 уровня)
EXPERIENCE_TABLE = {
    1: 0,
    2: 300,
    3: 900,
    4: 2700,
    5: 6500,
    6: 14000,
    7: 23000,
    8: 34000,
    9: 48000,
    10: 64000
}

def calculate_experience_reward(challenge_rating: float) -> int:
    """Расчет награды опытом"""
    base_exp = {
        0.125: 25, 0.25: 50, 0.5: 100, 1: 200,
        2: 450, 3: 700, 4: 1100, 5: 1800
    }
    return base_exp.get(challenge_rating, 0)
```

### Повышение уровня
```python
def level_up(character: Character) -> None:
    """Повышение уровня персонажа"""
    old_level = character.level
    new_level = old_level + 1
    
    # Увеличение максимального здоровья
    hit_die = character.class_hit_die
    con_mod = character.constitution_modifier
    hp_increase = hit_die + con_mod
    character.max_hp += hp_increase
    
    # Увеличение характеристик (на уровнях 4, 8)
    if new_level in [4, 8]:
        character.ability_score_improvement()
    
    # Новые способности класса
    new_features = character.class.get_features_for_level(new_level)
    for feature in new_features:
        character.add_feature(feature)
    
    # Увеличение профессионального бонуса
    if new_level in [5, 9]:
        character.proficiency_bonus += 1
```

### Увеличение характеристик
```python
def ability_score_improvement(character: Character) -> None:
    """Увеличение характеристик"""
    # Варианты:
    # 1. +2 к одной характеристике
    # 2. +1 к двум характеристикам
    
    choice = input("Выберите:\n1. +2 к одной характеристике\n2. +1 к двум характеристикам\n")
    
    if choice == "1":
        ability = select_ability()
        if character.abilities[ability] < 20:
            character.abilities[ability] += 2
    else:
        abilities = select_two_abilities()
        for ability in abilities:
            if character.abilities[ability] < 20:
                character.abilities[ability] += 1
```

---

## 💰 Торговая система

### Валюта
```python
class Currency:
    def __init__(self, gold: int = 0, silver: int = 0, copper: int = 0):
        self.gold = gold
        self.silver = silver
        self.copper = copper
    
    def to_copper(self) -> int:
        """Конвертация в медные монеты"""
        return self.gold * 100 + self.silver * 10 + self.copper
    
    @classmethod
    def from_copper(cls, total_copper: int) -> "Currency":
        """Создание из медных монет"""
        gold = total_copper // 100
        remaining = total_copper % 100
        silver = remaining // 10
        copper = remaining % 10
        return cls(gold, silver, copper)
```

### Торговец
```python
class Merchant:
    def __init__(self, name: str, inventory: dict, prices: dict):
        self.name = name
        self.inventory = inventory  # {item_id: quantity}
        self.prices = prices      # {item_id: price}
    
    def can_buy(self, item_id: str, quantity: int) -> bool:
        """Проверка возможности покупки"""
        return self.inventory.get(item_id, 0) >= quantity
    
    def get_price(self, item_id: str, quantity: int) -> int:
        """Получение цены"""
        base_price = self.prices.get(item_id, 0)
        return base_price * quantity
    
    def buy_item(self, character: Character, item_id: str, quantity: int) -> bool:
        """Покупка предмета"""
        total_price = self.get_price(item_id, quantity)
        
        if character.money.to_copper() < total_price:
            return False
        
        if not self.can_buy(item_id, quantity):
            return False
        
        # Проведение транзакции
        character.money = Currency.from_copper(
            character.money.to_copper() - total_price
        )
        self.inventory[item_id] -= quantity
        
        item = Item.create(item_id, quantity)
        character.inventory.add_item(item)
        
        return True
```

### Торговые операции
```python
def trade_transaction(buyer: Character, seller: Character, item: Item, price: int) -> bool:
    """Торговая транзакция между персонажами"""
    if buyer.money.to_copper() < price:
        return False
    
    if not seller.inventory.has_item(item.id, item.quantity):
        return False
    
    # Перемещение предмета
    seller.inventory.remove_item(item.id, item.quantity)
    buyer.inventory.add_item(item)
    
    # Перемещение денег
    buyer.money = Currency.from_copper(buyer.money.to_copper() - price)
    seller.money = Currency.from_copper(seller.money.to_copper() + price)
    
    return True
```

---

## 🏛️ Система репутации

### Фракции
```python
class Faction:
    def __init__(self, name: str, description: str, base_relations: dict):
        self.name = name
        self.description = description
        self.base_relations = base_relations  # Отношения с другими фракциями
    
    def get_reaction(self, reputation_score: int) -> str:
        """Получение реакции фракции"""
        if reputation_score >= 90:
            return "very_friendly"
        elif reputation_score >= 70:
            return "friendly"
        elif reputation_score >= 30:
            return "neutral"
        elif reputation_score >= 10:
            return "unfriendly"
        else:
            return "hostile"
```

### Репутация персонажа
```python
class ReputationSystem:
    def __init__(self):
        self.reputations = {}  # {character_id: {faction_id: score}}
    
    def change_reputation(self, character_id: str, faction_id: str, change: int) -> None:
        """Изменение репутации"""
        if character_id not in self.reputations:
            self.reputations[character_id] = {}
        
        current = self.reputations[character_id].get(faction_id, 50)
        new_score = max(0, min(100, current + change))
        self.reputations[character_id][faction_id] = new_score
    
    def get_reaction(self, character_id: str, faction_id: str) -> str:
        """Получение реакции фракции"""
        score = self.reputations.get(character_id, {}).get(faction_id, 50)
        return Faction.get_reaction_by_score(score)
```

### Влияние репутации
```python
def apply_reputation_effects(character: Character, faction: Faction) -> None:
    """Применение эффектов репутации"""
    reaction = character.get_reputation_with(faction.name)
    
    if reaction == "hostile":
        # Враждебные NPC атакуют при встрече
        character.add_status_effect("hated_by_" + faction.name)
    elif reaction == "friendly":
        # Дружественные цены в магазинах
        character.add_price_modifier(faction.name, 0.9)  # -10% цена
    elif reaction == "very_friendly":
        # Особые квесты и награды
        character.add_special_quests(faction.name)
```

---

## 🪄 Система заклинаний

### Структура заклинания
```python
class Spell:
    def __init__(self, spell_data: dict):
        self.name = spell_data["name"]
        self.level = spell_data["level"]
        self.school = spell_data["school"]
        self.casting_time = spell_data["casting_time"]
        self.range = spell_data["range"]
        self.components = spell_data["components"]
        self.duration = spell_data["duration"]
        self.description = spell_data["description"]
        
        # Механики
        self.requires_attack_roll = spell_data.get("requires_attack", False)
        self.save_type = spell_data.get("save_type")
        self.damage_type = spell_data.get("damage_type")
        self.damage_dice = spell_data.get("damage_dice")
```

### Слоты заклинаний
```python
class SpellSlots:
    def __init__(self, character_level: int, class_type: str):
        self.slots = self.calculate_slots(character_level, class_type)
        self.used = {level: 0 for level in self.slots}
    
    def calculate_slots(self, level: int, class_type: str) -> dict:
        """Расчет слотов заклинаний"""
        # Таблица для жреца/волшебника
        if class_type in ["cleric", "wizard"]:
            slot_table = {
                1: {1: 2},
                2: {1: 3},
                3: {1: 4, 2: 2},
                4: {1: 4, 2: 3},
                5: {1: 4, 2: 3, 3: 2},
                # ... до 10 уровня
            }
            return slot_table.get(level, {})
    
    def can_cast_spell(self, spell_level: int) -> bool:
        """Проверка доступности слота"""
        return self.used.get(spell_level, 0) < self.slots.get(spell_level, 0)
    
    def use_slot(self, spell_level: int) -> bool:
        """Использование слота"""
        if self.can_cast_spell(spell_level):
            self.used[spell_level] += 1
            return True
        return False
    
    def restore_slots(self) -> None:
        """Восстановление слотов (длинный отдых)"""
        self.used = {level: 0 for level in self.slots}
```

### Применение заклинаний
```python
def apply_spell_effect(spell: Spell, caster: Character, target: Character) -> SpellResult:
    """Применение эффекта заклинания"""
    result = SpellResult(spell=spell, caster=caster, target=target)
    
    if spell.damage_dice:
        damage = roll_dice(spell.damage_dice)
        if target.has_resistance(spell.damage_type):
            damage = damage // 2
        target.take_damage(damage)
        result.damage = damage
    
    if spell.save_type:
        save_dc = caster.spell_save_dc
        save_roll = d20() + target.get_save_modifier(spell.save_type)
        if save_roll < save_dc:
            # Провал спасброска - применить эффект
            apply_spell_status_effects(spell, target)
            result.save_failed = True
        else:
            result.save_passed = True
    
    return result
```

---

## 🎒 Инвентарь и предметы

### Предмет
```python
class Item:
    def __init__(self, item_data: dict):
        self.id = item_data["id"]
        self.name = item_data["name"]
        self.type = item_data["type"]  # weapon, armor, consumable, etc.
        self.rarity = item_data.get("rarity", "common")
        self.value = item_data.get("value", 0)
        self.weight = item_data.get("weight", 0)
        self.description = item_data.get("description", "")
        
        # Специфические свойства
        if self.type == "weapon":
            self.damage_dice = item_data["damage_dice"]
            self.damage_type = item_data["damage_type"]
            self.weapon_type = item_data["weapon_type"]
        elif self.type == "armor":
            self.armor_class = item_data["armor_class"]
            self.armor_type = item_data["armor_type"]
            self.stealth_disadvantage = item_data.get("stealth_disadvantage", False)
```

### Инвентарь
```python
class Inventory:
    def __init__(self, capacity: int = 20, max_weight: int = 150):
        self.items = {}  # {item_id: Item}
        self.quantities = {}  # {item_id: quantity}
        self.capacity = capacity
        self.max_weight = max_weight
    
    def add_item(self, item: Item, quantity: int = 1) -> bool:
        """Добавление предмета"""
        if len(self.items) >= self.capacity:
            return False
        
        current_weight = self.get_total_weight()
        item_weight = item.weight * quantity
        if current_weight + item_weight > self.max_weight:
            return False
        
        if item.id in self.items:
            self.quantities[item.id] += quantity
        else:
            self.items[item.id] = item
            self.quantities[item.id] = quantity
        
        return True
    
    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """Удаление предмета"""
        if item_id not in self.items:
            return False
        
        if self.quantities[item_id] < quantity:
            return False
        
        self.quantities[item_id] -= quantity
        
        if self.quantities[item_id] == 0:
            del self.items[item_id]
            del self.quantities[item_id]
        
        return True
    
    def get_total_weight(self) -> int:
        """Получение общего веса"""
        total = 0
        for item_id, item in self.items.items():
            total += item.weight * self.quantities[item_id]
        return total
```

### Hardcore режим инвентаря
```python
class HardcoreInventory(Inventory):
    """Инвентарь в hardcore режиме"""
    
    def __init__(self, strength_score: int):
        # Вместительность зависит от силы
        capacity = 10 + strength_score
        max_weight = strength_score * 15
        super().__init__(capacity, max_weight)
    
    def check_encumbrance(self) -> str:
        """Проверка перегрузки"""
        weight = self.get_total_weight()
        limit = self.max_weight
        
        if weight > limit:
            return "heavily_encumbered"  # Скорость 0, disadvantage на атаки
        elif weight > limit * 0.75:
            return "encumbered"  # Скорость -10 футов
        else:
            return "normal"
```

---

## 🎮 Примеры механик в действии

### Пример боя
```python
def combat_example():
    """Пример боевого сценария"""
    hero = Character.create_warrior("Арториус")
    goblin = Enemy.create_goblin()
    
    # Инициатива
    hero_init = roll_initiative(hero)
    goblin_init = roll_initiative(goblin)
    
    turn_order = sorted([
        ("hero", hero_init),
        ("goblin", goblin_init)
    ], key=lambda x: x[1], reverse=True)
    
    print(f"Порядок хода: {turn_order}")
    
    # Бой
    combat = Combat([hero, goblin])
    while not combat.is_finished():
        current = combat.get_current_turn()
        
        if current == "hero":
            # Ход героя
            result = attack(hero, goblin, hero.weapon)
            print(f"Арториус атакует: {result}")
        else:
            # Ход гоблина
            result = attack(goblin, hero, goblin.weapon)
            print(f"Гоблин атакует: {result}")
        
        combat.next_turn()
    
    print(f"Бой окончен! Победитель: {combat.get_winner()}")
```

### Пример торговли
```python
def trade_example():
    """Пример торговой операции"""
    merchant = Merchant.create_weapon_smith()
    hero = Character.create_fighter("Борис")
    
    # Покупка меча
    sword_price = merchant.get_price("longsword", 1)
    print(f"Цена меча: {sword_price} зм")
    
    if hero.money.to_copper() >= sword_price:
        success = merchant.buy_item(hero, "longsword", 1)
        if success:
            print("Меч куплен!")
            print(f"Осталось денег: {hero.money}")
        else:
            print("Ошибка покупки")
    else:
        print("Недостаточно денег")
```

---

## ⚙️ Настройки механик

### Конфигурация правил
```yaml
# game_rules.yaml
combat:
    critical_hit_multiplier: 2
    critical_miss_effect: "fumble"
    initiative_ties: "highest_dexterity"

experience:
    milestone_leveling: false
    training_required: true
    rest_requirements:
      short_rest: "1 hour"
      long_rest: "8 hours"

trading:
    price_variation: 0.1  # 10% вариация цен
    haggle_enabled: true
    reputation_discount: 0.2  # 20% скидка при дружелюбной репутации

hardcore_mode:
    inventory_encumbrance: true
    weapon_degradation: true
    death_permanent: false
    limited_rests: true
```

---

## 🧪 Тестирование систем

### Unit тесты
```python
def test_combat_attack():
    """Тест атаки в бою"""
    attacker = MockCharacter(strength=16, proficiency=2)
    target = MockCharacter(armor_class=15)
    weapon = MockWeapon(attack_bonus=2, damage_dice="1d8")
    
    # Мокируем бросок кубика
    with patch('random.randint', return_value=15):  # d20 = 15
        result = attack(attacker, target, weapon)
        
        # Атака: 15 + 2(str) + 2(prof) + 2(weapon) = 21
        # Попадание по КД 15
        assert result.hit == True
        assert result.damage > 0

def test_experience_calculation():
    """Тест расчета опыта"""
    assert calculate_experience_reward(0.25) == 50
    assert calculate_experience_reward(1) == 200
    assert calculate_experience_reward(3) == 700
```

---

*Игровые системы постоянно балансируются и улучшаются на основе обратной связи игроков*