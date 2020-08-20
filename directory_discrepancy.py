import os
import sys

dir1 = sys.argv[1]
dir2 = sys.argv[2]

files1 = set(os.listdir(dir1))
files2 = set(os.listdir(dir2))

print(f'In "{dir1}" but not in "{dir2}":')
print('=============================')
for discrepancy in sorted(files1.difference(files2)):
    print(discrepancy)

print()

print(f'In "{dir2}" but not in "{dir1}":')
print('=============================')
for discrepancy in sorted(files2.difference(files1)):
    print(discrepancy)
