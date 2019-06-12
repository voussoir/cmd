import sys

from voussoirkit import clipext

if len(sys.argv) == 1:
    sys.argv.append('!i')
text = clipext.resolve(sys.argv[1])
lines = text.splitlines()
digits = len(str(len(lines)))
form = '{no:>0%d} | {line}' % digits
for (index, line) in enumerate(lines):
    print(form.format(no=index+1, line=line))
