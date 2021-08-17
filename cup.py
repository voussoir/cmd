import pyperclip

from voussoirkit import pipeable

text = pipeable.input('!i', split_lines=False)
pyperclip.copy(text)
