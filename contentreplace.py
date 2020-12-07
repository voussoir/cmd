import argparse
import codecs
import os
import pyperclip
import re
import sys

from voussoirkit import interactive
from voussoirkit import pipeable
from voussoirkit import spinal
from voussoirkit import winglob


def contentreplace(filename, replace_from, replace_to, autoyes=False, do_regex=False):
    f = open(filename, 'r', encoding='utf-8')
    with f:
        content = f.read()

    if do_regex:
        occurances = len(re.findall(replace_from, content))
    else:
        occurances = content.count(replace_from)

    print(f'{filename}: Found {occurances} occurences.')
    if occurances == 0:
        return

    if not (autoyes or interactive.getpermission('Replace?')):
        return

    if do_regex:
        content = re.sub(replace_from, replace_to, content)
    else:
        content = content.replace(replace_from, replace_to)

    f = open(filename, 'w', encoding='utf-8')
    with f:
        f.write(content)

@pipeable.ctrlc_return1
def contentreplace_argparse(args):
    if args.recurse:
        files = spinal.walk_generator('.')
        files = (f for f in files if winglob.fnmatch(f.basename, args.filename_glob))
        filenames = (f.absolute_path for f in files)
    else:
        filenames = winglob.glob(args.filename_glob)
        filenames = [f for f in filenames if os.path.isfile(f)]

    if args.clip_prompt:
        replace_from = input('Ready from')
        if not replace_from:
            replace_from = pyperclip.paste()
        replace_to = input('Ready to')
        if not replace_to:
            replace_to = pyperclip.paste()
    else:
        replace_from = codecs.decode(args.replace_from, 'unicode_escape')
        if args.do_regex:
            replace_to = args.replace_to
        else:
            replace_to = codecs.decode(args.replace_to, 'unicode_escape')

    for filename in filenames:
        print(filename)
        contentreplace(
            filename,
            replace_from,
            replace_to,
            autoyes=args.autoyes,
            do_regex=args.do_regex,
        )

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('filename_glob')
    parser.add_argument('replace_from')
    parser.add_argument('replace_to')
    parser.add_argument('-y', '--yes', dest='autoyes', action='store_true', help='accept results without confirming')
    parser.add_argument('--recurse', dest='recurse', action='store_true')
    parser.add_argument('--regex', dest='do_regex', action='store_true')
    parser.add_argument('--clip_prompt', '--clip-prompt', dest='clip_prompt', action='store_true')
    parser.set_defaults(func=contentreplace_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
