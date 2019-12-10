'''
Used for executing slight variations on the same command.

usage:
resaw command arg1 arg2 {x} arg3

then x will be inputted from stdin every time.
The curly braces are required literally.
'''
import subprocess
import sys

if len(sys.argv) < 2:
    raise ValueError()

COMMAND = ' '.join('"%s"' % arg for arg in sys.argv[1:])
while True:
    x = input(':')
    command = COMMAND.format(x=x)
    print(command)
    subprocess.run(command, shell=True)
