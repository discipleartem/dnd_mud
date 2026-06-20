"""Тесты валидации ввода."""

from ui.input_handler import get_int_input, get_str_input


def test_get_int_input_valid_and_default(monkeypatch):
    """Валидное число и пустой ввод с default."""
    inputs = iter(["3", ""])
    monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))

    assert get_int_input("test: ", 0, 5) == 3
    assert get_int_input("test: ", 0, 5, default=2) == 2


def test_get_int_input_retries_out_of_range(monkeypatch, capsys):
    """Число вне диапазона — повторный запрос."""
    inputs = iter(["99", "2"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))

    assert get_int_input("test: ", 0, 5) == 2
    assert "Ошибка" in capsys.readouterr().out


def test_get_str_input_rejects_digits_and_short_name(monkeypatch, capsys):
    """only_letters и min_length отклоняют неверный ввод."""
    inputs = iter(["Hero1", "A", "Aragorn"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))

    result = get_str_input("name: ", min_length=2, only_letters=True)
    assert result == "Aragorn"
    output = capsys.readouterr().out
    assert output.count("Ошибка") == 2
