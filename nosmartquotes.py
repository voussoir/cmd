'''
no smart quotes
===============

Replace smart quotes and smart apostrophes with regular ASCII values.

Just say no to smart quotes!
'''
import argparse
import sys

from voussoirkit import betterhelp
from voussoirkit import spinal
from voussoirkit import vlogging

log = vlogging.getLogger(__name__, 'nosmartquotes')

def replace_smartquotes(text):
    text = text.replace('“', '"')
    text = text.replace('”', '"')
    text = text.replace('’', "'")
    text = text.replace('‘', "'")
    return text

def nosmartquotes_argparse(args):
    files = spinal.walk(
        glob_filenames=args.filename_glob,
        recurse=args.recurse,
    )

    for file in files:
        handle = file.open('r', encoding='utf-8')
        text = handle.read()
        handle.close()

        original_text = text
        text = replace_smartquotes(text)

        if text == original_text:
            continue

        handle = file.open('w', encoding='utf-8')
        handle.write(text)
        handle.close()
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