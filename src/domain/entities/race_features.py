# src/domain/entities/race_features.py
"""
Универсальная система обработки особенностей рас для D&D MUD.

Поддерживает различные типы особенностей:
- ability_choice: Выбор характеристик
- skill_choice: Выбор навыков
- feat_choice: Выбор черт
- trait: Пассивные черты
- proficiency: Владения
- spell: Заклинания
- language: Языки
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Union, TypedDict, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .race import Race


class FeatureData(TypedDict):
    """Данные особенности."""

    type: str
    name: str
    description: str
    max_choices: Optional[int]
    bonus_value: Optional[int]
    bonus: Optional[Dict[str, int]]
    traits: Optional[List[Dict[str, str]]]
    weapons: Optional[List[str]]
    skills: Optional[List[str]]
    spells: Optional[List[str]]
    languages: Optional[Dict[str, Union[List[str], int]]]
    choices: Optional[List[Union[str, int]]]


class RaceInfo(TypedDict):
    """Информация о расе."""

    name: str
    description: str
    short_description: str
    bonuses: str
    features: str


@dataclass
class FeatureProcessor:
    """Универсальный процессор особенностей рас."""

    @staticmethod
    def format_bonuses(
        bonuses: Dict[str, int],
        features: Optional[List[Dict[str, Union[str, int]]]] = None,
    ) -> str:
        """Форматирует бонусы к характеристикам с учетом особенностей.

        Args:
            bonuses: Базовые бонусы расы
            features: Список особенностей расы

        Returns:
            Отформатированная строка с бонусами
        """
        # Словарь с русскими названиями характеристик
        russian_names = {
            "strength": "Сила",
            "dexterity": "Ловкость",
            "constitution": "Телосложение",
            "intelligence": "Интеллект",
            "wisdom": "Мудрость",
            "charisma": "Харизма",
        }

        if not bonuses and not features:
            return "Нет бонусов"

        result_parts = []

        # Обрабатываем базовые бонусы
        if bonuses:
            for attr_name, bonus in bonuses.items():
                if bonus > 0:
                    # Используем словарь с русскими названиями
                    russian_name = russian_names.get(attr_name, attr_name.title())
                    bonus_str = f"+{bonus}"
                    result_parts.append(f"\t🎯 {russian_name}: {bonus_str}")

        # Обрабатываем особенности с выбором характеристик
        if features:
            for feature in features:
                if feature.get("type") == "ability_choice":
                    max_choices = feature.get("max_choices", 1)
                    bonus_value = feature.get("bonus_value", 1)
                    result_parts.append(
                        f"\t🎯 Бонусы: {max_choices} хар-ки (+{bonus_value} к каждой)"
                    )

        return "\n".join(result_parts) if result_parts else "Нет бонусов"

    @staticmethod
    def format_features(features: List[FeatureData]) -> List[str]:
        """Форматирует особенности для отображения.

        Args:
            features: Список особенностей

        Returns:
            Список отформатированных строк с особенностями
        """
        formatted = []

        for feature in features:
            feature_type = feature.get("type", "unknown")
            name = feature.get("name", "Неизвестная особенность")
            description = feature.get("description", "")

            if feature_type == "traits":
                # Обрабатываем составные черты
                traits = feature.get("traits", [])
                if traits:
                    for trait in traits:
                        trait_name = trait.get("name", "Неизвестная черта")
                        trait_desc = trait.get("description", "")
                        formatted.append(f"\t🎯 {trait_name}: {trait_desc}")
                else:
                    formatted.append(f"\t🎯 {name}: {description}")
            elif feature_type == "trait":
                formatted.append(f"\t🎯 {name}: {description}")
            elif feature_type == "proficiency":
                items = feature.get("weapons", feature.get("skills", []))
                if items:
                    items_str = (
                        ", ".join(items) if isinstance(items, list) else str(items)
                    )
                    formatted.append(f"\t⚔️ {name}: {items_str}")
                else:
                    formatted.append(f"\t⚔️ {name}: {description}")
            elif feature_type == "spell":
                spells = feature.get("spells", [])
                if spells:
                    spells_str = (
                        ", ".join(spells) if isinstance(spells, list) else str(spells)
                    )
                    formatted.append(f"\t🔮 {name}: {spells_str}")
                else:
                    formatted.append(f"\t🔮 {name}: {description}")
            elif feature_type == "language":
                languages = feature.get("languages", {})
                if languages:
                    base_langs = languages.get("base", [])
                    choice_count = languages.get("choice", 0)

                    if base_langs:
                        lang_str = (
                            ", ".join(base_langs)
                            if isinstance(base_langs, list)
                            else str(base_langs)
                        )
                        formatted.append(f"\t🌐 {name}: {lang_str}")

                    if isinstance(choice_count, int) and choice_count > 0:
                        formatted.append(f"\t🌐 {name}: {description}")
                else:
                    formatted.append(f"\t🌐 {name}: {description}")
            elif feature_type == "mask_wilderness":
                formatted.append(f"\t🌲 {name}: {description}")
            elif feature_type in ["ability_choice", "skill_choice", "feat_choice"]:
                formatted.append(f"\t⚙️ {name}: {description}")
            else:
                formatted.append(f"\t✨ {name}: {description}")

        return formatted

    @staticmethod
    def get_effective_bonuses(
        base_bonuses: Dict[str, int],
        subrace_bonuses: Dict[str, int] | None = None,
        inherit_bonuses: bool = True,
    ) -> Dict[str, int]:
        """Вычисляет эффективные бонусы с учетом наследования.

        Args:
            base_bonuses: Бонусы основной расы
            subrace_bonuses: Бонусы подрасы
            inherit_bonuses: Наследовать ли бонусы от основной расы

        Returns:
            Словарь с итоговыми бонусами
        """
        result = {}

        # Если наследуем бонусы, начинаем с базовых
        if inherit_bonuses:
            result.update(base_bonuses)

        # Добавляем бонусы подрасы
        if subrace_bonuses:
            result.update(subrace_bonuses)

        return result

    @staticmethod
    def get_all_features(
        base_features: List[FeatureData],
        subrace_features: Optional[List[FeatureData]] = None,
        inherit_features: bool = True,
    ) -> List[FeatureData]:
        """Получает все особенности с учетом наследования.

        Args:
            base_features: Особенности основной расы
            subrace_features: Особенности подрасы
            inherit_features: Наследовать ли особенности от основной расы

        Returns:
            Список всех особенностей
        """
        result = []

        # Если наследуем особенности, начинаем с базовых
        if inherit_features and base_features:
            result.extend(base_features)

        # Добавляем особенности подрасы
        if subrace_features:
            result.extend(subrace_features)

        return result


class RaceDisplayFormatter:
    """Форматировщик для отображения информации о расах."""

    def __init__(self) -> None:
        self.processor = FeatureProcessor()

    def format_race_info(
        self,
        race_data: Union[Dict[str, Union[str, int]], "Race"],
        subrace_key: Optional[str] = None,
    ) -> RaceInfo:
        """Форматирует полную информацию о расе для отображения.

        Args:
            race_data: Данные расы (ParsedRaceData или Dict из YAML)
            subrace_key: Ключ подрасы (опционально)

        Returns:
            Словарь с отформатированной информацией
        """
        # Словарь с русскими названиями характеристик
        russian_names = {
            "strength": "Сила",
            "dexterity": "Ловкость",
            "constitution": "Телосложение",
            "intelligence": "Интеллект",
            "wisdom": "Мудрость",
            "charisma": "Харизма",
        }

        # Обрабатываем подрасу
        subrace_bonuses: Dict[str, int] = {}
        subrace_features: List[Dict[str, Union[str, int]]] = []
        inherit_bonuses: bool = True
        inherit_features: bool = True

        if subrace_key:
            # Получаем данные подрасы из race_data
            if isinstance(race_data, dict):
                subraces_data: Any = race_data.get("subraces", {})
                if isinstance(subraces_data, dict) and subrace_key in subraces_data:
                    subrace = subraces_data[subrace_key]
                    name = subrace.get("name", "Неизвестная подраса")
                    description = subrace.get("description", "")
                    short_description = subrace.get("short_description", "")
                    raw_bonuses_subrace: Dict[str, Any] = subrace.get("bonuses", {})
                    # Преобразуем бонусы в целые числа
                    subrace_bonuses = {
                        k: int(v)
                        for k, v in raw_bonuses_subrace.items()
                        if isinstance(v, (int, str)) and str(v).isdigit()
                    }
                    raw_features: Any = subrace.get("features", [])
                    subrace_features = raw_features
                    inherit_bonuses = subrace.get("inherit_bonuses", True)
                    inherit_features = subrace.get("inherit_features", True)
                else:
                    # Подраса не найдена, используем базовые данные
                    name = race_data.get("name", "Неизвестная раса")
                    description = race_data.get("description", "")
                    short_description = race_data.get("short_description", "")
            else:
                # Для объекта Race используем базовые данные (упрощенная логика)
                name = getattr(race_data, "name", "Неизвестная раса")
                description = getattr(race_data, "description", "")
                short_description = getattr(race_data, "short_description", "")
        else:
            name = (
                race_data.get("name", "Неизвестная раса")
                if isinstance(race_data, dict)
                else getattr(race_data, "name", "Неизвестная раса")
            )
            description = (
                race_data.get("description", "")
                if isinstance(race_data, dict)
                else getattr(race_data, "description", "")
            )
            short_description = (
                race_data.get("short_description", "")
                if isinstance(race_data, dict)
                else getattr(race_data, "short_description", "")
            )

        # Получаем базовые данные
        base_bonuses: Dict[str, int] = {}
        base_features: List[Dict[str, Union[str, int]]] = []

        if isinstance(race_data, dict):
            raw_bonuses_base: Any = race_data.get("bonuses", {})
            # Преобразуем бонусы в целые числа
            base_bonuses = {
                k: int(v)
                for k, v in raw_bonuses_base.items()
                if isinstance(v, (int, str)) and str(v).isdigit()
            }  # type: ignore
            features_data: Any = race_data.get("features", [])
            base_features = (
                list(features_data) if isinstance(features_data, (list, tuple)) else []
            )
        else:
            base_bonuses = getattr(race_data, "bonuses", {})
            base_features = getattr(race_data, "features", [])

        # Вычисляем эффективные бонусы
        effective_bonuses = self.processor.get_effective_bonuses(
            base_bonuses, subrace_bonuses, inherit_bonuses
        )

        # Вычисляем все особенности
        # Преобразуем в правильный формат для FeatureProcessor
        base_features_converted: List[FeatureData] = []
        for feature in base_features:
            if isinstance(feature, dict):
                # Проверяем что все необходимые поля присутствуют
                base_feature_data: FeatureData = {
                    "name": str(feature.get("name", "")),
                    "description": str(feature.get("description", "")),
                    "type": str(feature.get("type", "")),
                    "bonus_value": (
                        int(feature.get("bonus_value", 0))
                        if feature.get("bonus_value") is not None
                        and str(feature.get("bonus_value")).isdigit()
                        else None
                    ),
                    "max_choices": (
                        int(feature.get("max_choices", 0))
                        if feature.get("max_choices") is not None
                        and str(feature.get("max_choices")).isdigit()
                        else None
                    ),
                    "choices": (
                        list(feature.get("choices", []))  # type: ignore[arg-type]
                        if feature.get("choices") is not None
                        and isinstance(feature.get("choices"), (list, tuple))
                        else None
                    ),
                    "bonus": None,
                    "traits": None,
                    "weapons": None,
                    "skills": None,
                    "spells": None,
                    "languages": None,
                }
                base_features_converted.append(base_feature_data)

        subrace_features_converted: List[FeatureData] = []
        for feature in subrace_features:
            if isinstance(feature, dict):
                # Проверяем что все необходимые поля присутствуют
                subrace_feature_data: FeatureData = {
                    "name": str(feature.get("name", "")),
                    "description": str(feature.get("description", "")),
                    "type": str(feature.get("type", "")),
                    "bonus_value": (
                        int(feature.get("bonus_value", 0))
                        if feature.get("bonus_value") is not None
                        and str(feature.get("bonus_value")).isdigit()
                        else None
                    ),
                    "max_choices": (
                        int(feature.get("max_choices", 0))
                        if feature.get("max_choices") is not None
                        and str(feature.get("max_choices")).isdigit()
                        else None
                    ),
                    "choices": (
                        list(feature.get("choices", []))  # type: ignore[arg-type]
                        if feature.get("choices") is not None
                        and isinstance(feature.get("choices"), (list, tuple))
                        else None
                    ),
                    "bonus": None,
                    "traits": None,
                    "weapons": None,
                    "skills": None,
                    "spells": None,
                    "languages": None,
                }
                subrace_features_converted.append(subrace_feature_data)

        all_features = self.processor.get_all_features(
            base_features_converted, subrace_features_converted, inherit_features
        )

        # Форматируем бонусы
        bonus_parts = []
        for attr_name, bonus in effective_bonuses.items():
            if bonus > 0:
                russian_name = russian_names.get(attr_name, attr_name.title())
                bonus_str = f"+{bonus}"
                bonus_parts.append(f"\t🎯 {russian_name}: {bonus_str}")

        bonuses_str = "\n".join(bonus_parts) if bonus_parts else ""

        # Форматируем особенности
        features_list = self.processor.format_features(all_features)
        features_str = (
            "\n".join(feature for feature in features_list) if features_list else ""
        )

        return {
            "name": name,
            "description": description,
            "short_description": short_description,
            "bonuses": bonuses_str,
            "features": features_str,
        }

    def _get_short_description(
        self, description: str, yaml_short_desc: str | None = None
    ) -> str:
        """Получает короткое описание из полного или из YAML поля.

        Args:
            description: Полное описание расы
            yaml_short_desc: Короткое описание из YAML (опционально)

        Returns:
            Короткое описание
        """
        # Если в YAML есть короткое описание, используем его
        if yaml_short_desc:
            return yaml_short_desc

        # Иначе генерируем из полного (старая логика)
        if not description:
            return "Описание отсутствует"

        # Разделяем на предложения
        sentences = description.split(".")

        # Берем первые 1-2 предложения
        short_sentences = []
        for sentence in sentences[:2]:
            sentence = sentence.strip()
            if sentence:
                short_sentences.append(sentence)

        short_desc = ". ".join(short_sentences)
        if short_desc and not short_desc.endswith("."):
            short_desc += "."

        return short_desc if short_desc else "Описание отсутствует"
