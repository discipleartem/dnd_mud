# Примеры кода по архитектуре

Этот документ содержит практические примеры реализации архитектурных паттернов в проекте D&D MUD.

---

## 🏗️ Value Objects (Entities Layer)

### BaseValidatable - базовый класс для всех VO

```python
# src/value_objects/base_validatable.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

class BaseValidatable(ABC):
    """Базовый класс для всех валидируемых объектов."""
    
    @abstractmethod
    def validate(self) -> None:
        """Валидация бизнес-правил."""
        pass
    
    def is_valid(self) -> bool:
        """Проверка валидности."""
        try:
            self.validate()
            return True
        except (ValueError, TypeError):
            return False
    
    def __post_init__(self) -> None:
        """Автовалидация после создания."""
        self.validate()
```

### Language Value Object

```python
# src/value_objects/language.py
from dataclasses import dataclass
from .base_validatable import BaseValidatable

@dataclass
class Language(BaseValidatable):
    """Value Object для языка."""
    code: str
    name: str
    
    def validate(self) -> None:
        """Валидация языка."""
        if not isinstance(self.code, str):
            raise TypeError("Language code must be string")
        
        if len(self.code) != 2:
            raise ValueError("Language code must be exactly 2 characters")
        
        if not self.code.isalpha():
            raise ValueError("Language code must contain only letters")
        
        if not isinstance(self.name, str):
            raise TypeError("Language name must be string")
        
        if len(self.name.strip()) == 0:
            raise ValueError("Language name cannot be empty")
        
        if len(self.name) > 50:
            raise ValueError("Language name too long (max 50 characters)")
    
    @property
    def display_name(self) -> str:
        """Отображаемое имя."""
        return f"{self.name} ({self.code.upper()})"
```

### WelcomeContent Value Object

```python
# src/value_objects/welcome_content.py
from dataclasses import dataclass
from typing import List
from .base_validatable import BaseValidatable

@dataclass
class WelcomeContent(BaseValidatable):
    """Контент приветствия."""
    title: str
    subtitle: str
    messages: List[str]
    
    def validate(self) -> None:
        """Валидация контента."""
        if not isinstance(self.title, str):
            raise TypeError("Title must be string")
        
        if len(self.title.strip()) == 0:
            raise ValueError("Title cannot be empty")
        
        if len(self.title) > 100:
            raise ValueError("Title too long (max 100 characters)")
        
        if not isinstance(self.subtitle, str):
            raise TypeError("Subtitle must be string")
        
        if len(self.subtitle) > 150:
            raise ValueError("Subtitle too long (max 150 characters)")
        
        if not isinstance(self.messages, list):
            raise TypeError("Messages must be list")
        
        if len(self.messages) == 0:
            raise ValueError("At least one message is required")
        
        if len(self.messages) > 10:
            raise ValueError("Too many messages (max 10)")
        
        for i, message in enumerate(self.messages):
            if not isinstance(message, str):
                raise TypeError(f"Message {i} must be string")
            if len(message) > 200:
                raise ValueError(f"Message {i} too long (max 200 characters)")
```

---

## 🎯 Use Cases Layer

### WelcomeService

```python
# src/services/welcome_service.py
from typing import Optional
from ..value_objects.language import Language
from ..value_objects.welcome_content import WelcomeContent

class WelcomeService:
    """Сервис приветствия пользователя."""
    
    def __init__(self, content: WelcomeContent):
        self.content = content
    
    def get_welcome_message(self, language: Language) -> str:
        """Получить локализованное приветствие."""
        # Бизнес-логика выбора языка
        if language.code == "ru":
            return f"{self.content.title}\n{self.content.subtitle}"
        else:
            return f"{self.content.title}\n{self.content.subtitle}"
    
    def get_messages_count(self) -> int:
        """Получить количество сообщений."""
        return len(self.content.messages)
    
    def get_message_by_index(self, index: int) -> str:
        """Получить сообщение по индексу."""
        if not 0 <= index < len(self.content.messages):
            raise ValueError(f"Message index {index} out of range")
        
        return self.content.messages[index]
    
    def validate_content(self) -> bool:
        """Валидация контента."""
        return self.content.is_valid()
```

### CharacterService (планируется)

```python
# src/services/character_service.py (пример для будущего)
from typing import Optional
from ..value_objects.character import Character
from ..value_objects.race import Race
from ..value_objects.character_class import CharacterClass

class CharacterService:
    """Сервис работы с персонажами."""
    
    def create_character(self, name: str, race: Race, 
                        character_class: CharacterClass) -> Character:
        """Создание нового персонажа."""
        # Бизнес-логика создания персонажа
        character = Character(
            name=name,
            race=race,
            character_class=character_class,
            level=1,
            experience=0
        )
        
        # Применение расовых бонусов
        self._apply_race_bonuses(character, race)
        
        # Применение бонусов класса
        self._apply_class_bonuses(character, character_class)
        
        return character
    
    def _apply_race_bonuses(self, character: Character, race: Race) -> None:
        """Применение расовых бонусов."""
        for ability, bonus in race.ability_bonuses.items():
            current_value = character.abilities.get(ability, 10)
            character.abilities[ability] = current_value + bonus
    
    def _apply_class_bonuses(self, character: Character, 
                           character_class: CharacterClass) -> None:
        """Применение бонусов класса."""
        character.hit_points = character_class.hit_die + character.abilities.get(
            "constitution", 10
        ) // 2 - 5
```

---

## 🔄 DTO Layer

### WelcomeDTO

```python
# src/welcome_dto.py
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class WelcomeDTO:
    """DTO для передачи данных между слоями."""
    language_code: str
    user_name: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь."""
        return {
            "language_code": self.language_code,
            "user_name": self.user_name,
            "preferences": self.preferences or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WelcomeDTO":
        """Создание из словаря."""
        return cls(
            language_code=data["language_code"],
            user_name=data.get("user_name"),
            preferences=data.get("preferences")
        )

@dataclass
class WelcomeResponseDTO:
    """DTO для ответа."""
    title: str
    subtitle: str
    messages: list
    status: str
    language_code: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь."""
        return {
            "title": self.title,
            "subtitle": self.subtitle,
            "messages": self.messages,
            "status": self.status,
            "language_code": self.language_code
        }
```

---

## 🔌 Interface Adapters Layer

### WelcomeAdapter

```python
# src/console/welcome_adapter.py
from typing import Dict, Any
from ..services.welcome_service import WelcomeService
from ..value_objects.language import Language
from ..utils.translation_loader import TranslationLoader
from ..welcome_dto import WelcomeDTO, WelcomeResponseDTO

class WelcomeAdapter:
    """Адаптер для консольного вывода приветствия."""
    
    def __init__(self, welcome_service: WelcomeService,
                 translation_loader: TranslationLoader):
        self.welcome_service = welcome_service
        self.translation_loader = translation_loader
    
    def process_welcome_request(self, dto: WelcomeDTO) -> WelcomeResponseDTO:
        """Обработать запрос приветствия."""
        try:
            # Создание объекта языка
            language = Language(dto.language_code, 
                               self._get_language_name(dto.language_code))
            
            # Получение приветствия через сервис
            welcome_message = self.welcome_service.get_welcome_message(language)
            
            # Загрузка локализованных сообщений
            translations = self.translation_loader.load_translations(
                dto.language_code
            )
            
            # Формирование ответа
            return WelcomeResponseDTO(
                title=translations.get("welcome", {}).get("title", "Welcome"),
                subtitle=translations.get("welcome", {}).get("subtitle", ""),
                messages=self.welcome_service.content.messages,
                status="success",
                language_code=dto.language_code
            )
            
        except Exception as e:
            # Обработка ошибок
            return WelcomeResponseDTO(
                title="Error",
                subtitle=str(e),
                messages=[],
                status="error",
                language_code=dto.language_code
            )
    
    def display_welcome(self, response_dto: WelcomeResponseDTO) -> None:
        """Отобразить приветствие в консоли."""
        print(f"\n{response_dto.title}")
        print(f"{response_dto.subtitle}")
        print("-" * 50)
        
        for message in response_dto.messages:
            print(f"  {message}")
    
    def _get_language_name(self, code: str) -> str:
        """Получить название языка."""
        language_names = {
            "ru": "Русский",
            "en": "English"
        }
        return language_names.get(code, "Unknown")
```

---

## 🛠️ Framework Layer

### TranslationLoader

```python
# src/utils/translation_loader.py
import json
from pathlib import Path
from typing import Dict, Any

class TranslationLoader:
    """Загрузчик переводов из JSON файлов."""
    
    def __init__(self, base_path: str = "data/translations"):
        self.base_path = Path(base_path)
    
    def load_translations(self, language_code: str) -> Dict[str, Any]:
        """Загрузить переводы для языка."""
        file_path = self.base_path / f"{language_code}.json"
        
        if not file_path.exists():
            raise FileNotFoundError(f"Translation file not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in translation file: {e}")
        except Exception as e:
            raise RuntimeError(f"Error loading translation file: {e}")
    
    def get_available_languages(self) -> list[str]:
        """Получить список доступных языков."""
        if not self.base_path.exists():
            return []
        
        languages = []
        for file_path in self.base_path.glob("*.json"):
            languages.append(file_path.stem)
        
        return sorted(languages)
    
    def validate_translation_structure(self, translations: Dict[str, Any]) -> bool:
        """Валидация структуры переводов."""
        required_sections = ["welcome", "menu", "game"]
        
        for section in required_sections:
            if section not in translations:
                return False
        
        return True
```

### GameDataLoader

```python
# src/utils/game_data_loader.py
import yaml
from pathlib import Path
from typing import Dict, Any, List

class GameDataLoader:
    """Загрузчик игровых данных из YAML файлов."""
    
    def __init__(self, base_path: str = "data"):
        self.base_path = Path(base_path)
    
    def load_races(self) -> Dict[str, Any]:
        """Загрузить данные о расах."""
        return self._load_yaml_file("races.yaml")
    
    def load_classes(self) -> Dict[str, Any]:
        """Загрузить данные о классах."""
        return self._load_yaml_file("classes.yaml")
    
    def load_abilities(self) -> Dict[str, Any]:
        """Загрузить данные о способностях."""
        return self._load_yaml_file("abilities.yaml")
    
    def load_backgrounds(self) -> Dict[str, Any]:
        """Загрузить данные о предысториях."""
        return self._load_yaml_file("backgrounds.yaml")
    
    def _load_yaml_file(self, filename: str) -> Dict[str, Any]:
        """Загрузить YAML файл."""
        file_path = self.base_path / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"Game data file not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in game data file: {e}")
        except Exception as e:
            raise RuntimeError(f"Error loading game data file: {e}")
    
    def validate_race_data(self, races: Dict[str, Any]) -> bool:
        """Валидация данных о расах."""
        if "races" not in races:
            return False
        
        for race_key, race_data in races["races"].items():
            if not isinstance(race_data, dict):
                return False
            
            required_fields = ["name", "description"]
            for field in required_fields:
                if field not in race_data:
                    return False
        
        return True
```

---

## 🧪 Тесты по архитектуре

### Unit тесты для Value Objects

```python
# tests/test_value_objects.py
import pytest
from src.value_objects.language import Language
from src.value_objects.welcome_content import WelcomeContent

class TestLanguage:
    """Тесты для Language Value Object."""
    
    def test_valid_language_creation(self):
        """Тест создания валидного языка."""
        language = Language("ru", "Русский")
        assert language.code == "ru"
        assert language.name == "Русский"
        assert language.is_valid()
    
    def test_invalid_language_code_length(self):
        """Тест невалидной длины кода языка."""
        with pytest.raises(ValueError, match="Language code must be exactly 2"):
            Language("rus", "Русский")
    
    def test_invalid_language_code_chars(self):
        """Тест невалидных символов в коде языка."""
        with pytest.raises(ValueError, match="Language code must contain only letters"):
            Language("r1", "Русский")
    
    def test_empty_language_name(self):
        """Тест пустого названия языка."""
        with pytest.raises(ValueError, match="Language name cannot be empty"):
            Language("ru", "")
    
    def test_display_name_property(self):
        """Тест свойства display_name."""
        language = Language("ru", "Русский")
        assert language.display_name == "Русский (RU)"

class TestWelcomeContent:
    """Тесты для WelcomeContent Value Object."""
    
    def test_valid_content_creation(self):
        """Тест создания валидного контента."""
        content = WelcomeContent(
            title="Welcome",
            subtitle="To D&D MUD",
            messages=["Hello", "World"]
        )
        assert content.title == "Welcome"
        assert content.is_valid()
    
    def test_empty_title(self):
        """Тест пустого заголовка."""
        with pytest.raises(ValueError, match="Title cannot be empty"):
            WelcomeContent("", "Subtitle", ["Message"])
    
    def test_no_messages(self):
        """Тест отсутствия сообщений."""
        with pytest.raises(ValueError, match="At least one message is required"):
            WelcomeContent("Title", "Subtitle", [])
```

### Интеграционные тесты для сервисов

```python
# tests/test_services_integration.py
import pytest
from src.services.welcome_service import WelcomeService
from src.value_objects.welcome_content import WelcomeContent
from src.value_objects.language import Language

class TestWelcomeServiceIntegration:
    """Интеграционные тесты для WelcomeService."""
    
    @pytest.fixture
    def welcome_content(self):
        """Фикстура с контентом."""
        return WelcomeContent(
            title="Test Title",
            subtitle="Test Subtitle", 
            messages=["Message 1", "Message 2"]
        )
    
    @pytest.fixture
    def welcome_service(self, welcome_content):
        """Фикстура с сервисом."""
        return WelcomeService(welcome_content)
    
    def test_get_welcome_message_ru(self, welcome_service):
        """Тест получения русского приветствия."""
        language = Language("ru", "Русский")
        message = welcome_service.get_welcome_message(language)
        assert "Test Title" in message
        assert "Test Subtitle" in message
    
    def test_get_messages_count(self, welcome_service):
        """Тест получения количества сообщений."""
        assert welcome_service.get_messages_count() == 2
    
    def test_get_message_by_index(self, welcome_service):
        """Тест получения сообщения по индексу."""
        message = welcome_service.get_message_by_index(0)
        assert message == "Message 1"
    
    def test_invalid_message_index(self, welcome_service):
        """Тест невалидного индекса сообщения."""
        with pytest.raises(ValueError, match="Message index 5 out of range"):
            welcome_service.get_message_by_index(5)
```

---

Эти примеры демонстрируют правильное применение архитектурных паттернов в проекте и служат руководством для разработки новых компонентов.
