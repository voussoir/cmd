import argparse
import os
import sys

from voussoirkit import betterhelp
from voussoirkit import pathclass
from voussoirkit import pipeable
from voussoirkit import spinal
from voussoirkit import vlogging

log = vlogging.getLogger(__name__, 'nosmartquotes')

THIS_FILE = os.path.abspath(__file__)

def replace_smartquotes(text):
    text = text.replace('“', '"')
    text = text.replace('”', '"')
    text = text.replace('’', "'")
    text = text.replace('‘', "'")
    return text

def nosmartquotes_argparse(args):
    globs = list(pipeable.input_many(args.patterns))
    files = spinal.walk(
        glob_filenames=globs,
        exclude_filenames={THIS_FILE},
        recurse=args.recurse,
    )

    for file in files:
        text = file.read('r', encoding='utf-8')

        original_text = text
        text = replace_smartquotes(text)

        if text == original_text:
            continue

        file.write('w', text, encoding='utf-8')
        pipeable.stdout(file.absolute_path)

    return 0

@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser(
        description='''
        Replace smart quotes and smart apostrophes with regular ASCII values.

        Just say no to smart quotes!
        ''',
    )
    parser.examples = [
        '*.md --recurse',
    ]
    parser.add_argument(
        'patterns',
        nargs='+',
        help='''
        One or more glob patterns for input files.
        ''',
    )
    parser.add_argument(
        '--recurse',
        action='store_true',
        help='''
        If provided, recurse into subdirectories and process those files too.
        ''',
    )
    parser.set_defaults(func=nosmartquotes_argparse)

    return betterhelp.go(parser, argv)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
