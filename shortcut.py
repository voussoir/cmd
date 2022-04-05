import argparse
import sys
import winshell

from voussoirkit import betterhelp
from voussoirkit import pathclass
from voussoirkit import subproctools

def shortcut(lnk_name, target, start_in=None, icon=None):
    lnk = pathclass.Path(lnk_name)
    if lnk.extension != 'lnk':
        lnk = lnk.add_extension('lnk')

    lnk.assert_not_exists()

    (target, args) = (target[0], target[1:])
    target = pathclass.Path(target)
    target.assert_exists()

    if start_in is not None:
        start_in = pathclass.Path(start_in)
        start_in.assert_is_directory()

    if icon is not None:
        icon = pathclass.Path(icon)
        icon.assert_is_file()

    shortcut = winshell.Shortcut(lnk.absolute_path)
    shortcut.path = target.absolute_path

    if args:
        shortcut.arguments = subproctools.format_command(args)
    if start_in is not None:
        shortcut.working_directory = start_in.absolute_path
    if icon is not None:
        shortcut.icon_location = (icon.absolute_path, 0)

    shortcut.write()
    return lnk

def shortcut_argparse(args):
    try:
        lnk = shortcut(
            lnk_name=args.lnk_name,
            target=args.target,
            start_in=args.start_in,
            icon=args.icon,
        )
        print(lnk.absolute_path)
        return 0
    except pathclass.Exists:
        print(f'{args.lnk_name} already exists.')
        return 1

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.examples = [
        'game.lnk --icon game.ico -- javaw.exe -jar game.jar',
        'game.lnk --icon game.ico -- 4 8 6',
    ]

    parser.add_argument(
        'lnk_name',
        help='''
        The filepath of the lnk file you want to create.
        ''',
    )
    parser.add_argument(
        'target',
        nargs='+',
        help='''
        The filepath of the target file and any additional arguments separated
        by spaces. If you want to include an argument that starts with hyphens,
        consider putting this last and use `--` to indicate the end of named
        arguments, since they might otherwise be mistaken for arguments to this
        program.
        ''',
    )
    parser.add_argument(
        '--start_in',
        '--start-in',
        '--startin',
        default=None,
        help='''
        Directory to use as CWD for the program.
        ''',
    )
    parser.add_argument(
        '--icon',
        default=None,
        help='''
        Path to an .ico file.
        ''',
    )
    parser.set_defaults(func=shortcut_argparse)

    return betterhelp.go(parser, argv)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
