"""
Watchdog - отслеживание изменений файлов
"""
import time
import logging
from pathlib import Path
from typing import Callable, Dict, List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent


class GameFileHandler(FileSystemEventHandler):
    """Обработчик событий файловой системы"""

    def __init__(self, callback: Callable, debounce_seconds: float = 1.0):
        super().__init__()
        self.callback = callback
        self.debounce_seconds = debounce_seconds
        self.logger = logging.getLogger(__name__)

        # Debounce механизм
        self._last_modified: Dict[str, float] = {}

    def on_modified(self, event: FileSystemEvent):
        """Вызывается при изменении файла"""
        if event.is_directory:
            return

        file_path = event.src_path
        current_time = time.time()

        # Проверяем debounce
        if file_path in self._last_modified:
            time_diff = current_time - self._last_modified[file_path]
            if time_diff < self.debounce_seconds:
                return

        self._last_modified[file_path] = current_time

        # Обрабатываем только нужные файлы
        if self._should_process(file_path):
            self.logger.info(f"Обнаружено изменение файла: {file_path}")
            try:
                self.callback(file_path, 'modified')
            except Exception as e:
                self.logger.error(f"Ошибка обработки изменения файла: {e}")

    def on_created(self, event: FileSystemEvent):
        """Вызывается при создании файла"""
        if event.is_directory:
            return

        file_path = event.src_path
        if self._should_process(file_path):
            self.logger.info(f"Создан новый файл: {file_path}")
            try:
                self.callback(file_path, 'created')
            except Exception as e:
                self.logger.error(f"Ошибка обработки нового файла: {e}")

    def on_deleted(self, event: FileSystemEvent):
        """Вызывается при удалении файла"""
        if event.is_directory:
            return

        file_path = event.src_path
        if self._should_process(file_path):
            self.logger.info(f"Удален файл: {file_path}")
            try:
                self.callback(file_path, 'deleted')
            except Exception as e:
                self.logger.error(f"Ошибка обработки удаления файла: {e}")

    def _should_process(self, file_path: str) -> bool:
        """Проверка нужно ли обрабатывать файл"""
        extensions = ['.yaml', '.yml', '.json']
        return any(file_path.endswith(ext) for ext in extensions)


class WatchdogManager:
    """Менеджер отслеживания файлов"""

    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.enabled = config_manager.get('watchdog.enabled', True)
        self.debounce = config_manager.get('watchdog.debounce_seconds', 1.0)
        self.logger = logging.getLogger(__name__)

        self.observer: Observer = None
        self._handlers: List[FileSystemEventHandler] = []
        self._callbacks: Dict[str, List[Callable]] = {
            'config': [],
            'data': [],
            'mods': []
        }

    def initialize(self):
        """Инициализация watchdog"""
        if not self.enabled:
            self.logger.info("Watchdog отключен в конфигурации")
            return

        self.logger.info("Инициализация Watchdog")
        self.observer = Observer()

    def add_callback(self, watch_type: str, callback: Callable):
        """
        Добавить callback для определенного типа отслеживания

        Args:
            watch_type: Тип ('config', 'data', 'mods')
            callback: Функция callback
        """
        if watch_type in self._callbacks:
            self._callbacks[watch_type].append(callback)

    def start_watching(self):
        """Запуск отслеживания"""
        if not self.enabled or not self.observer:
            return

        # Отслеживание конфига
        if self.config_manager.get('watchdog.watch_config', True):
            self._watch_path(
                Path('config'),
                'config',
                "Отслеживание конфигурации"
            )

        # Отслеживание данных
        if self.config_manager.get('watchdog.watch_data', True):
            data_path = Path(self.config_manager.get('paths.base_data'))
            self._watch_path(
                data_path,
                'data',
                "Отслеживание игровых данных"
            )

        # Отслеживание модов
        if self.config_manager.get('watchdog.watch_mods', True):
            mods_path = Path(self.config_manager.get('paths.mods'))
            self._watch_path(
                mods_path,
                'mods',
                "Отслеживание модификаций"
            )

        # Запускаем observer
        try:
            self.observer.start()
            self.logger.info("Watchdog запущен")
        except Exception as e:
            self.logger.error(f"Ошибка запуска Watchdog: {e}")

    def _watch_path(self, path: Path, watch_type: str, log_message: str):
        """Настройка отслеживания директории"""
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

        def callback(file_path: str, event_type: str):
            for cb in self._callbacks[watch_type]:
                cb(file_path, event_type)

        handler = GameFileHandler(callback, self.debounce)
        self._handlers.append(handler)

        self.observer.schedule(handler, str(path), recursive=True)
        self.logger.info(f"{log_message}: {path}")

    def stop_watching(self):
        """Остановка отслеживания"""
        if self.observer and self.observer.is_alive():
            self.observer.stop()
            self.observer.join(timeout=5)
            self.logger.info("Watchdog остановлен")

    def is_running(self) -> bool:
        """Проверка работает ли watchdog"""
        return self.observer and self.observer.is_alive()