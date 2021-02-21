'''
I create my own icon files for some file types. This script edits the windows
registry to assign the file extension icon and optionally a human-friendly name
string. Must run as administrator.

WARNING, if the extension is already associated with a program, or is otherwise
connected to a progid, this will break it.
'''
import argparse
import sys
import winreg

from voussoirkit import interactive
from voussoirkit import pathclass

def extension_registry(ico_file, human_name=None):
    if ico_file.extension != 'ico':
        raise ValueError('Must provide a .ico file.')

    name = ico_file.replace_extension('').basename

    dot_ex = f'.{name}'
    hash_ex = f'#{name}'

    prompt = [
        f'Set {dot_ex} = {hash_ex}',
        f'Set {hash_ex}\\DefaultIcon = {ico_file.absolute_path}',
    ]

    if human_name:
        prompt.append(f'Set {hash_ex} = {human_name}')

    prompt = '\n'.join(prompt)

    if not interactive.getpermission(prompt):
        return

    dot_key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, dot_ex)
    winreg.SetValueEx(dot_key, '', 0, winreg.REG_SZ, hash_ex)

    hash_key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, hash_ex)
    if human_name:
        winreg.SetValueEx(hash_key, '', 0, winreg.REG_SZ, human_name)

    icon_key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f'{hash_ex}\\DefaultIcon')
    winreg.SetValueEx(icon_key, '', 0, winreg.REG_SZ, ico_file.absolute_path)

    print('Finished.')


def extension_registry_argparse(args):
    return extension_registry(
        ico_file=pathclass.Path(args.ico_file),
        human_name=args.name,
    )

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('ico_file')
    parser.add_argument('--name', default=None)
    parser.set_defaults(func=extension_registry_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
