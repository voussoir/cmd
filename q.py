import argparse
import hashlib
import os
import re
import sys
import time
import traceback

# make this on your pythonpath like this:
# EXTENSION_COMMANDS = {
#     'ytqueue': ('youtube-dl', '{id}'),
# }
import qcommands

from voussoirkit import backoff
from voussoirkit import betterhelp
from voussoirkit import dotdict
from voussoirkit import operatornotify
from voussoirkit import pathclass
from voussoirkit import vlogging

log = vlogging.getLogger(__name__, 'q')

# When no more queuefiles are discovered, the program will sleep for increasing
# amounts of time to reduce the amount of disk activity.
sleeping_backoff = backoff.Linear(m=1, b=10, max=600)

# Each file gets an individual backoff object when it encounters an error, so
# we can continue processing other files while and come back to the problematic
# ones later, with increasing timeouts.
error_backoffs = {}

# If a file demonstrates unrecoverable errors, we blacklist it and never touch
# it again. If the file ever disappears then we remove it from the blacklist.
error_blacklist = set()

def filter_collaborate(files, collaborate):
    if collaborate is None:
        return files

    newfiles = []
    for file in files:
        bits = int(hashlib.md5(file.basename.encode('utf-8')).hexdigest(), 16)
        if ((bits % collaborate.mod) + 1) == collaborate.mine:
            newfiles.append(file)
    return newfiles

def get_extension_command(extension):
    for (key, (command, argument)) in qcommands.EXTENSION_COMMANDS.items():
        if isinstance(key, str):
            if key == extension:
                return (command, argument)
            continue
        match = re.match(key, extension)
        if not match:
            continue
        groups = match.groups()
        if not groups:
            return (command, argument)
        command = re.sub(key, command, extension)
        return (command, argument)

def handle_blacklist(file, reason=''):
    if reason:
        log.warning('%s is blacklisted because:\n%s', file.absolute_path, reason)
    else:
        log.warning('%s is blacklisted.', file.absolute_path)

    error_blacklist.add(file)

def handle_failure(file):
    err_bo = error_backoffs.get(file)
    if err_bo is None:
        err_bo = backoff.Linear(m=3600, b=3600, max=86400)
        error_backoffs[file] = err_bo

    if (err_bo.x % 3) == 1:
        log.warning('%s is having repeated problems.', file.absolute_path)

    timeout = err_bo.next()
    log.info('%s is in time out for %d.', file.absolute_path, timeout)
    err_bo.expire_at = time.time() + timeout

def override_extension_commands(extension, command):
    extension = extension.lower().strip('.')

    if command:
        command = [f'"{x}"' if ' ' in x else x for x in command]
        command = ' '.join(command).strip()
    else:
        command = qcommands.EXTENSION_COMMANDS[extension]

    qcommands.EXTENSION_COMMANDS.clear()
    qcommands.EXTENSION_COMMANDS[extension] = command

def parse_collaborate(collaborate):
    if collaborate is None:
        return None

    collaborate = collaborate.strip()
    if not collaborate:
        return None

    (mod, mine) = collaborate.split('.')
    if mod == 1:
        return None

    mod = int(mod)
    mine = int(mine)
    if mine == 0:
        raise ValueError('Collaborate values are 1-indexed, don\'t use 0.')
    collaborate = dotdict.DotDict(mod=mod, mine=mine)
    return collaborate

def process_file(file, args=None):
    # Race condition
    if not file.exists:
        return

    if file in error_blacklist:
        return

    err_bo = error_backoffs.get(file)
    if err_bo is not None and time.time() < err_bo.expire_at:
        return

    extension = file.extension.no_dot.lower()

    if not get_extension_command(extension):
        return

    ############################################################################

    sleeping_backoff.reset()

    commands = []

    if file.size > 0:
        links = read_file_links(file)
        (command, argument) = get_extension_command(extension)
        commands.extend(f'{command} "{link}"' for link in links)

    else:
        (command, argument) = get_extension_command(extension)
        base = file.replace_extension('').basename
        argument = argument.format(id=base)
        commands.append(f'{command} {argument}')

    exit_code = 0

    for command in commands:
        log.info(f'Handling {file.basename} with `{command}`')

        exit_code = os.system(command)
        if exit_code != 0:
            handle_failure(file)
            break

    if exit_code == 0:
        try:
            os.remove(file)
        except FileNotFoundError:
            # Race condition
            pass
        except PermissionError:
            handle_blacklist(file, reason=traceback.format_exc())

def prune_blacklist():
    if not error_blacklist:
        return

    for file in list(error_blacklist):
        if not file.exists:
            error_blacklist.remove(file)

def prune_error_backoffs():
    if not error_backoffs:
        return

    now = time.time()

    for (file, err_bo) in list(error_backoffs.items()):
        if not file.exists:
            error_backoffs.pop(file)
            continue

def read_file_links(file):
    links = file.open('r').read().splitlines()
    links = (l.strip() for l in links)
    links = (l for l in links if l)
    links = (l for l in links if not l.startswith('#'))
    return links

def queue_once(folders, collaborate=None):
    log.info(time.strftime('%H:%M:%S Looking for files.'))
    files = []
    for folder in folders:
        try:
            files.extend(folder.listdir_files())
        except Exception as exc:
            log.warning('listdir %s raised:\ntraceback.format_exc()', folder)

    files = filter_collaborate(files, collaborate)

    for file in files:
        process_file(file)

    prune_error_backoffs()
    prune_blacklist()

def queue_forever(folders, collaborate=None):
    while True:
        queue_once(folders, collaborate=collaborate)
        time.sleep(sleeping_backoff.next())

def q_argparse(args):
    if args.extension:
        override_extension_commands(args.extension, args.command)

    if args.folders:
        folders = [pathclass.Path(d) for d in args.folders]
    else:
        folders = [pathclass.cwd()]

    for folder in folders:
        folder.assert_is_directory()

    if args.once:
        queue_once(folders=folders)
        return 0

    try:
        queue_forever(folders=folders, collaborate=args.collaborate)
    except KeyboardInterrupt:
        return 0

@operatornotify.main_decorator(subject='q.py', notify_every_line=True)
@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('extension', nargs='?', default=None)
    parser.add_argument('command', nargs='*', default=None)
    parser.add_argument('--folders', nargs='*', default=None)
    parser.add_argument(
        '--once',
        dest='once',
        action='store_true',
        help='''
        Process queuefiles until there are none left, then stop the program.
        ''',
    )
    parser.add_argument(
        '--collaborate',
        dest='collaborate',
        default=None,
        type=parse_collaborate,
        metavar='mod.mine',
        help='''
        Due to youtube download throttling, I want to run multiple q processes
        to download multiple videos simultaneously, but I don't necessarily want to
        deal with multiprocess management within this program because each process
        makes lots of console output. So the idea is that we run multiple copies of
        this file with different --collaborate settings and they collaboratively
        partition the files amongst themselves. Another way of doing this is to put
        the queuefiles into separate folders and run one process per folder, but
        that puts the burden on the side that creates the queuefiles.
        The way this argument works is two numbers separated by a period: `mod.mine`.
        All of the q processes should have the same number for `mod`, and each
        process should have a different number for `mine`, counting 1, 2, 3,
        until mod.
        If you want to collaborate with three processes, you'd use
        --collaborate 3.1 for one instance, --collaborate 3.2 for the second, and
        --collaborate 3.3 for the third.
        ''',
    )
    parser.set_defaults(func=q_argparse)

    return betterhelp.go(parser, argv)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
