'''
watchforlinks
=============

This program will continuously watch your clipboard for URLs and save them to
individual files. The files will have randomly generated names. The current
contents of your clipboard will be erased.

> watchforlinks [extension] <flags>

extension:
    The saved files will have this extension.
    If not provided, the default is "generic".

flags:
--regex X:
    A regex pattern. Only URLs that match this pattern will be saved.
'''
import argparse
import pyperclip
import re
import sys
import time

from voussoirkit import betterhelp
from voussoirkit import passwordy
from voussoirkit import pathclass
from voussoirkit import pipeable

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

    path = pathclass.Path(passwordy.random_hex(12)).add_extension(extension)
    pyperclip.copy('')
    pipeable.stdout(f'{path.basename} {text}')
    path.write('w', text, encoding='utf-8')

def loop_forever(extension, regex):
    pyperclip.copy('')
    while True:
        loop_once(extension=extension, regex=regex)
        time.sleep(1)

def watchforlinks_argparse(args):
    pipeable.stderr('Watching clipboard... Press Ctrl+C to stop.')
    try:
        loop_forever(extension=args.extension, regex=args.regex)
    except KeyboardInterrupt:
        pass
    return 0

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('extension', nargs='?', default='generic')
    parser.add_argument('--regex', default=None)
    parser.set_defaults(func=watchforlinks_argparse)

    return betterhelp.single_main(argv, parser, __doc__)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
