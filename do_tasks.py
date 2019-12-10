'''
Execute the contents of all .task files forever.
'''
import argparse
import os
import send2trash
import sys
import time


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
        do_tasks(task_files)
        try:
            time.sleep(10)
        except KeyboardInterrupt:
            break

def do_tasks_argparse(args):
    if args.task_files:
        return do_tasks(args.task_files)

    if args.only_once:
        return do_tasks(get_task_files())

    return do_tasks_forever()

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('task_files', nargs='*', default=None)
    parser.add_argument('--once', dest='only_once', action='store_true')
    parser.set_defaults(func=do_tasks_argparse)

    args = parser.parse_args(argv)
    args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
