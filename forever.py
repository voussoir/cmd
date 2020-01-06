import subprocess
import sys

cmd = sys.argv[1:]
while True:
    subprocess.run(cmd, shell=True)
