'''
Execute the contents of all .task files forever.
'''
import argparse
import os
import send2trash
import sys
import time

from voussoirkit import backoff
from voussoirkit import operatornotify
from voussoirkit import vlogging

log = vlogging.get_logger(__name__, 'do_tasks')

bo = backoff.Linear(m=1, b=5, max=1800)

def get_task_files():
    return [f for f in os.listdir() if (os.path.isfile(f) and f.endswith('.task'))]

def do_tasks(task_files):
    for task_file in task_files:
        if not os.path.exists(task_file):
            continue
        with open(task_file, 'r', encoding='utf-8') as handle:
            task_content = handle.read()
        task_content = task_content.strip()
        print('TASK:', task_content)
        status = os.system(task_content)
        if status == 0:
            send2trash.send2trash(task_file)

def do_tasks_forever():
    while True:
        print(time.strftime('%H:%M:%S'), 'Looking for tasks.')
        task_files = get_task_files()
        if task_files:
            bo.reset()
        do_tasks(task_files)
        try:
            time.sleep(bo.next())
        except KeyboardInterrupt:
            break

def do_tasks_argparse(args):
    if args.task_files:
        return do_tasks(args.task_files)

    if args.only_once:
        return do_tasks(get_task_files())

    return do_tasks_forever()

@operatornotify.main_decorator(subject='do_tasks')
@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('task_files', nargs='*', default=None)
    parser.add_argument('--once', dest='only_once', action='store_true')
    parser.set_defaults(func=do_tasks_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
