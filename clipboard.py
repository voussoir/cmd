'''
Dump the clipboard to stdout. I use this for redirecting to files.
'''
import argparse
import pyperclip
import sys

def clipboard_argparse(args):
    if args.output_file:
        open(args.output_file, 'w', encoding='utf-8').write(pyperclip.paste())
    else:
        text = pyperclip.paste()
        text = text.replace('\r', '')
        print(text)

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('-o', '--output', dest='output_file', default=None)
    parser.set_defaults(func=clipboard_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
