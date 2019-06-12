import os

from voussoirkit import pipeable


for line in pipeable.go():
    os.system(line)
