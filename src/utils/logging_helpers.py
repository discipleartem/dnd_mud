"""Утилиты для логирования.

Содержит общие функции логирования, используемые во всем проекте.
Следует DRY принципу - Don't Repeat Yourself.
"""

import logging
from typing import Any

# Настраиваем базовый логгер
logger = logging.getLogger(__name__)


def log_info(message: str, **kwargs: Any) -> None:
    """Записать информационное сообщение в лог."""
    if kwargs:
        logger.info(message, **kwargs)
    else:
        logger.info(message)


def log_error(message: str, **kwargs: Any) -> None:
    """Записать сообщение об ошибке в лог."""
    if kwargs:
        logger.error(message, **kwargs)
    else:
        logger.error(message)


def log_debug(message: str, **kwargs: Any) -> None:
    """Записать отладочное сообщение в лог."""
    if kwargs:
        logger.debug(message, **kwargs)
    else:
        logger.debug(message)


def log_warning(message: str, **kwargs: Any) -> None:
    """Записать предупреждение в лог."""
    if kwargs:
        logger.warning(message, **kwargs)
    else:
        logger.warning(message)


def setup_basic_logging(level: str = "INFO") -> None:
    """Настроить базовое логирование.

    Args:
        level: Уровень логирования (DEBUG, INFO, WARNING, ERROR)
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
