import argparse
import pyperclip
import sys
import time

from voussoirkit import passwordy
from voussoirkit import pathclass

def loop_once(extension):
    try:
        text = pyperclip.paste()
    except Exception:
        return

    text = text.strip()

    if len(text.split(sep=None, maxsplit=1)) > 1:
        return

    if 'http://' in text or 'https://' in text:
        path = pathclass.Path(passwordy.urandom_hex(12)).add_extension(extension)
        pyperclip.copy('')
        print(path.basename, text)
        h = open(path.absolute_path, 'w', encoding='utf-8')
        h.write(text)
        h.close()

def loop_forever(extension):
    while True:
        loop_once(extension=extension)
        time.sleep(1)

def watchforlinks_argparse(args):
    try:
        loop_forever(extension=args.extension)
    except KeyboardInterrupt:
        pass

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('extension', nargs='?', default='generic')
    parser.set_defaults(func=watchforlinks_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
