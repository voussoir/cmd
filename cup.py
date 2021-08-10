import pyperclip

from voussoirkit import pipeable

text = '\n'.join(pipeable.input('!i'))
pyperclip.copy(text)
