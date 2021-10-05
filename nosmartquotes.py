'''
no smart quotes
===============

Replace smart quotes and smart apostrophes with regular ASCII values.

Just say no to smart quotes!
'''
import argparse
import os
import sys

from voussoirkit import betterhelp
from voussoirkit import pathclass
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
    files = spinal.walk(
        glob_filenames=args.filename_glob,
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
        print(file.absolute_path)

    return 0

@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('filename_glob')
    parser.add_argument('--recurse', action='store_true')
    parser.set_defaults(func=nosmartquotes_argparse)

    return betterhelp.single_main(argv, parser, __doc__)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
