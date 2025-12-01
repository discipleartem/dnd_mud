"""
tests/test_window_manager.py
"""


class TestWindowManager:
    """Тесты для WindowManager"""

    def test_initialization(self):
        """Тест инициализации WindowManager"""
        from ui.window_manager import WindowManager

        wm = WindowManager()

        assert wm.width > 0
        assert wm.height > 0

    def test_get_size(self):
        """Тест получения размеров окна"""
        from ui.window_manager import WindowManager

        wm = WindowManager()
        width, height = wm.get_size()

        assert isinstance(width, int)
        assert isinstance(height, int)
        assert width > 0
        assert height > 0

    def test_wrap_text(self):
        """Тест переноса текста"""
        from ui.window_manager import WindowManager

        wm = WindowManager()

        text = "This is a very long line that should be wrapped to multiple lines when the width is small"
        wrapped = wm.wrap_text(text, width=40)

        lines = wrapped.split('\n')
        for line in lines:
            assert len(line) <= 40

    def test_center_text(self):
        """Тест центрирования текста"""
        from ui.window_manager import WindowManager

        wm = WindowManager()

        text = "Centered"
        centered = wm.center_text(text)

        # Проверяем что текст содержится в результате
        assert text in centered