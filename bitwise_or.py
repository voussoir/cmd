import argparse
import sys

from voussoirkit import betterhelp
from voussoirkit import interactive
from voussoirkit import pathclass
from voussoirkit import pipeable
from voussoirkit import vlogging

log = vlogging.getLogger(__name__, 'bitwise_or')

CHUNK_SIZE = 2**20

def bitwise_or_argparse(args):
    patterns = pipeable.input_many(args.files, skip_blank=True, strip=True)
    files = list(pathclass.glob_many_files(patterns))

    if len(files) < 2:
        log.fatal('Need at least two input files.')
        return 1

    output = pathclass.Path(args.output)
    if output.is_dir:
        log.fatal('Output path "%s" is a directory.', args.output)
        return 1

    if any(output == file for file in files):
        log.fatal('Output cannot be one of the inputs.')
        return 1

    if not output.exists:
        pass
    elif args.overwrite:
        pass
    elif not pipeable.in_tty():
        return 1
    elif not interactive.getpermission(f'Overwrite "{output.absolute_path}"?'):
        return 1

    handles = [file.open('rb') for file in files]
    output_handle = output.open('wb')
    while True:
        chunk = 0
        length = 1
        for handle in handles[:]:
            read = handle.read(CHUNK_SIZE)
            length = max(length, len(read))
            if not read:
                handles.remove(handle)
            chunk |= int.from_bytes(read, 'big')
        if not handles:
            break
        output_handle.write(chunk.to_bytes(length, 'big'))
    pipeable.stdout(output.absolute_path)

@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser(
        description='''
        Merge two or more files by performing bitwise or on their bits.
        That is, every byte of the output file will be the bitwise or of the
        corresponding byte from all of the input files.
        ''',
    )

    parser.add_argument('files', nargs='+')
    parser.add_argument('--output', required=True, type=pathclass.Path)
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='''
        Provide this flag if the output file already exists and you'd like to
        overwrite it.
        ''',
    )
    parser.set_defaults(func=bitwise_or_argparse)

    return betterhelp.go(parser, argv)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
