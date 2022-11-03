from voussoirkit import pipeable

for line in pipeable.go(skip_blank=True):
    pipeable.stdout(line)
