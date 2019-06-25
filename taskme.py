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

task_command = ' '.join('"%s"' % arg for arg in sys.argv[1:])
task_command = f'cd /d {os.getcwd()} & {task_command}'

timestamp = f'{time.time()}'.replace('.', '').ljust(18, '0')
filename = f'C:\\tasks\\{timestamp}-{random.randint(1, 1000000)}.task'

with open(filename, 'w', encoding='utf-8') as handle:
    handle.write(task_command)
