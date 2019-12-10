'''
Create a task file to be executed by do_tasks.

Usage:
taskme command arg1 arg2
'''
import sys
import time
import random
import os

if len(sys.argv) < 2:
    raise ValueError()

task_line = sys.argv[1:]
task_command = task_line[0]
if ' ' in task_command:
    task_command = '"%s"' % task_command
task_arguments = task_line[1:]
for (index, arg) in enumerate(task_arguments):
    if arg not in ['&', '&&']:
        task_arguments[index] = '"%s"' % arg
task_arguments = ' '.join(task_arguments)

task_command = f'cd /d "{os.getcwd()}" & {task_command} {task_arguments}'

timestamp = f'{time.time():<019}'.replace('.', '')
randid = f'{random.randint(1, 1000000):>06}'
filename = f'C:\\tasks\\{timestamp}-{randid}.task'

with open(filename, 'w', encoding='utf-8') as handle:
    handle.write(task_command)
