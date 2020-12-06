import argparse
import sys
import winshell

from voussoirkit import pathclass

def shortcut(lnk_name, target, start_in=None, icon=None):
    lnk = pathclass.Path(lnk_name)
    if lnk.extension != 'lnk':
        lnk = lnk.add_extension('lnk')

    lnk.assert_not_exists()

    target = pathclass.Path(target)
    target.assert_exists()

    if start_in is not None:
        start_in = pathclass.Path(start_in)
        start_in.assert_is_directory()

    if icon is not None:
        icon = pathclass.Path(icon)
        icon.assert_is_file()

    lnk = winshell.Shortcut(lnk.absolute_path)
    lnk.path = target.absolute_path
    if start_in is not None:
        lnk.working_directory = start_in.absolute_path
    if icon is not None:
        lnk.icon_location = (icon.absolute_path, 0)

    lnk.write()

def shortcut_argparse(args):
    return shortcut(
        lnk_name=args.lnk_name,
        target=args.target,
        start_in=args.start_in,
        icon=args.icon,
    )

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('lnk_name')
    parser.add_argument('target')
    parser.add_argument('--start_in', '--start-in', '--startin', dest='start_in', default=None)
    parser.add_argument('--icon', dest='icon', default=None)
    parser.set_defaults(func=shortcut_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
