'''
reg_extension_icon
==================

This script edits the windows registry HKEY_CLASSES_ROOT to assign a file
extension icon and optionally a human-friendly name string.

Must run as administrator.

WARNING, if the extension is already associated with a program, or is otherwise
connected to a progid, this will break it.

> reg_extension_icon ico_file <flags>

ico_file:
    Filepath of the icon file.

--extension:
    If you omit this option, your file should be named "png.ico" or "py.ico" to
    set the icon for png and py types. If the name of your ico file is not the
    name of the extension you want to control, specify the extension here.

--name:
    A human-friendly name string which will show on Explorer under the "Type"
    column and in the properties dialog.
'''
import argparse
import sys
import winreg

from voussoirkit import betterhelp
from voussoirkit import interactive
from voussoirkit import pathclass

def extension_registry(ico_file, extension=None, human_name=None):
    if ico_file.extension != 'ico':
        raise ValueError('Must provide a .ico file.')

    if extension is None:
        extension = ico_file.replace_extension('').basename
    else:
        extension = extension.strip('.')

    dot_ex = f'.{extension}'
    hash_ex = f'#{extension}'

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
        extension=args.extension,
        human_name=args.name,
    )

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('ico_file')
    parser.add_argument('--extension', default=None)
    parser.add_argument('--name', default=None)
    parser.set_defaults(func=extension_registry_argparse)

    return betterhelp.single_main(argv, parser, __doc__)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
