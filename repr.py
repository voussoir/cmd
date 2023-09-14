from voussoirkit import pipeable

for line in pipeable.go():
    pipeable.stdout(repr(line))
