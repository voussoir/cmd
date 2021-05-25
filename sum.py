from voussoirkit import pipeable


total = sum(float(x) for x in pipeable.go() if x.strip())
pipeable.stdout(f'{total}\n')
