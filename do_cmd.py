import os

from voussoirkit import pipeable

for line in pipeable.go(strip=True, skip_blank=True):
    os.system(line)
