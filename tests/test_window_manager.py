import pytest
from src.core.window_manager import WindowManager

def test_singleton():
    wm1 = WindowManager()
    wm2 = WindowManager()
    assert wm1 is wm2

def test_get_terminal_size():
    wm = WindowManager()
    size = wm.get_terminal_size()
    assert size.width >= 80
    assert size.height >= 24

def test_wrap_text():
    wm = WindowManager()
    text = "This is a very long text that needs to be wrapped"
    lines = wm.wrap_text(text, width=20)
    assert all(len(line) <= 20 for line in lines)