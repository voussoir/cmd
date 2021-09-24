import sys

from voussoirkit import pipeable

lines = pipeable.input(sys.argv[1])
replace_from = sys.argv[2]
replace_to = sys.argv[3]

for line in lines:
    pipeable.stdout(line.replace(replace_from, replace_to))
