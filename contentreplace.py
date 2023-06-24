import argparse
import codecs
import pyperclip
import re
import sys

from voussoirkit import betterhelp
from voussoirkit import interactive
from voussoirkit import pathclass
from voussoirkit import pipeable
from voussoirkit import spinal
from voussoirkit import vlogging

log = vlogging.getLogger(__name__, 'contentreplace')

def contentreplace(file, replace_from, replace_to, autoyes=False, do_regex=False):
    file = pathclass.Path(file)
    content = file.read('r', encoding='utf-8')

    if do_regex:
        occurances = len(re.findall(replace_from, content, flags=re.MULTILINE))
    else:
        occurances = content.count(replace_from)

    print(f'{file.absolute_path}: Found {occurances} occurences.')
    if occurances == 0:
        return

    if not (autoyes or interactive.getpermission('Replace?')):
        return

    if do_regex:
        content = re.sub(replace_from, replace_to, content, flags=re.MULTILINE)
    else:
        content = content.replace(replace_from, replace_to)

    file.write('w', content, encoding='utf-8')

@pipeable.ctrlc_return1
def contentreplace_argparse(args):
    files = spinal.walk(
        glob_filenames=args.filename_glob,
        recurse=args.recurse,
    )

    if args.clip_prompt:
        replace_from = input('Ready from')
        if not replace_from:
            replace_from = pyperclip.paste()
        replace_to = input('Ready to')
        if not replace_to:
            replace_to = pyperclip.paste()
    else:
        if args.do_regex:
            replace_from = args.replace_from
            replace_to = args.replace_to
        else:
            replace_from = codecs.decode(args.replace_from, 'unicode_escape')
            replace_to = codecs.decode(args.replace_to, 'unicode_escape')

    for file in files:
        try:
            contentreplace(
                file,
                replace_from,
                replace_to,
                autoyes=args.autoyes,
                do_regex=args.do_regex,
            )
        except UnicodeDecodeError:
            log.error('%s encountered unicode decode error.', file.absolute_path)

    return 0

@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser(
        description='''
        find-and-replace en masse
        ''',
    )
    parser.add_argument(
        'filename_glob',
        help='''
        A glob pattern that targets the files of interest.
        ''',
    )
    parser.add_argument(
        'replace_from',
        help='''
        String to be replaced. You can use backslash-escaped symbols like
        \\n for newline.
        ''',
    )
    parser.add_argument(
        'replace_to',
        help='''
        String with which to replace. Can use backslash-escaped symbols.
        ''',
    )
    parser.add_argument(
        '--yes',
        dest='autoyes',
        action='store_true',
        help='''
        If provided, replacements will occur automatically without prompting.
        ''',
    )
    parser.add_argument(
        '--recurse',
        action='store_true',
        help='''
        If provided, we will recurse into subdirectories and look for glob matches
        there too. If not provided, only files in the cwd are affected.
        ''',
    )
    parser.add_argument(
        '--regex',
        dest='do_regex',
        action='store_true',
        help='''
        If provided, the given replace_from, replace_to will be treated as regex
        strings. If not provided, we use regular str.replace.
        ''',
    )
    parser.add_argument(
        '--clip_prompt',
        '--clip-prompt',
        action='store_true',
        help='''
        If you want to do contentreplace with unicode that is difficult to enter
        into your terminal, or multi-line strings that don't work as command line
        arguments, this option might help you. The program will wait for you to put
        the text of interest into your clipboard and press Enter.
        ''',
    )
    parser.set_defaults(func=contentreplace_argparse)

    return betterhelp.go(parser, argv)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
