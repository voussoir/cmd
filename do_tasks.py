'''
Execute the contents of all .task files forever.
'''
import os
import sys
import time

def main(args=None):
    if args:
        task_files = args
        do_loop = False
    else:
        do_loop = True

    while True:
        if do_loop:
            task_files = [f for f in os.listdir() if (os.path.isfile(f) and f.endswith('.task'))]
        for task_file in task_files:
            with open(task_file, 'r', encoding='utf-8') as handle:
                task_content = handle.read()
            task_content = task_content.strip()
            print('TASK:', task_content)
            status = os.system(task_content)
            if status == 0:
                os.remove(task_file)
        if not do_loop:
            break
        time.sleep(10)


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
