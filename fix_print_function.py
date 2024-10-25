import textwrap
import shutil

def wrap_print(text, width=None):
    if width is None:
        width, _ = shutil.get_terminal_size()
    wrapped_text = textwrap.fill(text, width=width)
    print(wrapped_text)