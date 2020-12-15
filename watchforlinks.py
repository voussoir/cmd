import argparse
import pyperclip
import re
import sys
import time

from voussoirkit import passwordy
from voussoirkit import pathclass

def loop_once(extension, regex=None):
    try:
        text = pyperclip.paste()
    except Exception:
        return

    text = text.strip()

    if len(text.split(sep=None, maxsplit=1)) > 1:
        return

    if 'http://' not in text and 'https://' not in text:
        return

    if regex and not re.search(regex, text):
        return

    path = pathclass.Path(passwordy.urandom_hex(12)).add_extension(extension)
    pyperclip.copy('')
    print(path.basename, text)
    h = path.open('w', encoding='utf-8')
    h.write(text)
    h.close()

def loop_forever(extension, regex):
    pyperclip.copy('')
    while True:
        loop_once(extension=extension, regex=regex)
        time.sleep(1)

def watchforlinks_argparse(args):
    try:
        loop_forever(extension=args.extension, regex=args.regex)
    except KeyboardInterrupt:
        pass

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('extension', nargs='?', default='generic')
    parser.add_argument('--regex', dest='regex', default=None)
    parser.set_defaults(func=watchforlinks_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
