import argparse
import os
import shlex
import subprocess
import sys
import tempfile

from voussoirkit import betterhelp
from voussoirkit import pipeable
from voussoirkit import subproctools
from voussoirkit import winwhich
from voussoirkit import vlogging

log = vlogging.getLogger(__name__, 'tempeditor')

class NoEditor(Exception):
    pass

class BadStatus(Exception):
    pass

def tempeditor(initial_text=None):
    editor = os.environ.get('EDITOR')
    if not editor:
        raise NoEditor('You do not have an EDITOR variable.')

    command = shlex.split(editor)
    command[0] = winwhich.which(command[0])

    file = tempfile.TemporaryFile('r+', encoding='utf-8', prefix='tempeditor-', delete=False)
    command.append(file.name)

    if initial_text:
        file.write(initial_text)

    # The text editor may not be allowed to write to the file while Python has
    # the file handle, so let's close it and re-open after the user is finished.
    file.close()

    status = subprocess.check_call(command)
    if status == 0:
        handle = open(file.name, 'r', encoding='utf-8')
        text = handle.read()
        handle.close()

    try:
        os.remove(file.name)
    except Exception:
        pass

    if status == 0:
        return text
    else:
        raise BadStatus(subproctools.format_command(command), status)

def tempeditor_argparse(args):
    if args.initial_text is None:
        initial_text = None
    else:
        initial_text = pipeable.input(args.initial_text, split_lines=False)

    try:
        text = tempeditor(initial_text=initial_text)
        pipeable.stdout(text)
        return 0
    except NoEditor as exc:
        log.fatal(exc)
        return 1
    except BadStatus as exc:
        log.fatal(f'Command {exc.args[0]} returned status {exc.args[1]}.')
        return 1

@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser(
        description='''
        This program allows you to use your preferred text editor as an
        intermediate step in a processing pipeline. The user will use the text
        editor to edit a temp file, and when they close the editor the contents
        of the temp file will be sent to stdout.
        ''',
    )

    parser.add_argument(
        '--text',
        dest='initial_text',
        default=None,
        type=str,
        help='''
        The initial text in the document.
        Uses pipeable to support !c clipboard, !i stdin.
        If not provided, the user starts with a blank document.
        ''',
    )
    parser.set_defaults(func=tempeditor_argparse)

    return betterhelp.go(parser, argv)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
