"""Адаптивный вывод текста с учётом ширины терминала."""

import shutil

from colorama import Fore, Style


def get_terminal_width() -> int:
    """Определить текущую ширину терминала.

    Returns:
        Ширина в символах (минимум 40)
    """
    size = shutil.get_terminal_size(fallback=(80, 24))
    return max(size.columns, 40)


def print_wrapped(
    text: str,
    color: str = '',
    width: int | None = None,
    indent: int = 0,
) -> None:
    """Вывести текст с автоматическим переносом по ширине терминала.

    Args:
        text: Текст для вывода
        color: Цвет colorama (например Fore.YELLOW)
        width: Ширина вывода (если None — определяется автоматически)
        indent: Отступ слева в пробелах
    """
    if width is None:
        width = get_terminal_width() - 2  # запас на границы

    max_line_len = width - indent
    if max_line_len < 10:
        max_line_len = 10

    prefix = ' ' * indent

    lines = text.split('\n')
    output_lines: list[str] = []

    for line in lines:
        while len(line) > max_line_len:
            # Ищем пробел для разрыва
            break_pos = line.rfind(' ', 0, max_line_len)
            if break_pos == -1:
                # Нет пробела — режем по max_line_len
                break_pos = max_line_len
            output_lines.append(prefix + line[:break_pos])
            line = line[break_pos:].lstrip()
        output_lines.append(prefix + line)

    final_text = '\n'.join(output_lines)
    print(f'{color}{final_text}{Style.RESET_ALL}')


def print_header(
    text: str,
    width: int | None = None,
    fill_char: str = '=',
) -> None:
    """Вывести заголовок в рамке из fill_char.

    Args:
        text: Текст заголовка (центрируется)
        width: Ширина рамки
        fill_char: Символ рамки
    """
    if width is None:
        width = get_terminal_width() - 2

    # Если текст длиннее ширины — просто выводим без рамки
    if len(text) > width - 4:
        print_wrapped(text, color=Fore.YELLOW)
        return

    line = fill_char * width
    padded = f'  {text}  '
    centered = padded.center(width)

    print(f'{Fore.YELLOW}{line}{Style.RESET_ALL}')
    print(f'{Fore.YELLOW}{centered}{Style.RESET_ALL}')
    print(f'{Fore.YELLOW}{line}{Style.RESET_ALL}')