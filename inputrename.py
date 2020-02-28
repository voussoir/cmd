import os
import sys

from voussoirkit import winglob

keyword = sys.argv[1]
pattern = f'*{keyword}*'

files = winglob.glob(pattern)
for file in files:
    print(file)
    this = input('>')
    if this:
        os.rename(file, file.replace(keyword, this))
