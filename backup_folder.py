import argparse
import rarpar
import sys
import time

from voussoirkit import pathclass

def backup_folder_argparse(args):
    date = time.strftime('%Y-%m-%d')

    folder = pathclass.Path(args.folder)
    rar_name = f'{folder.basename} {date}'

    rarpar.rarpar(
        path=folder,
        basename=rar_name,
        compression=rarpar.COMPRESSION_MAX,
        dictionary_size='128m',
        rec=5,
        solid=True,
        workdir=args.destination_folder,
    )

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('folder')
    parser.add_argument('destination_folder')
    parser.set_defaults(func=backup_folder_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
