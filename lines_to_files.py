import argparse
import sys

from voussoirkit import gentools
from voussoirkit import pathclass

def linestofiles(file, lines_per_file):
    file = pathclass.Path(file)
    basename = file.replace_extension('').basename
    basename = basename + '_{index}'
    folder = file.parent
    handle = file.open('r', encoding='utf-8')
    chunks = gentools.chunk_generator(handle, lines_per_file)
    for (index, chunk) in enumerate(chunks):
        chunk = ''.join(chunk)
        chunk_file = folder.with_child(basename.format(index=index)).add_extension(file.extension)
        print(chunk_file)
        chunk_file.open('w', encoding='utf-8').write(chunk)
    handle.close()

def linestofiles_argparse(args):
    return linestofiles(args.file, args.lines_per_file)

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('file')
    parser.add_argument('lines_per_file', type=int)
    parser.set_defaults(func=linestofiles_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
