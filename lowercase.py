import sys

from voussoirkit import pipeable


for line in pipeable.go():
    pipeable.output(line.lower())
