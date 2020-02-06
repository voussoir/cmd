from voussoirkit import spinal

basenames = {}

walker = spinal.walk_generator('.', yield_directories=True, yield_files=False)
for directory in walker:
    basenames.setdefault(directory.basename, []).append(directory)

for (basename, dupes) in basenames.items():
    if len(dupes) == 1:
        continue
    for dupe in dupes:
        print(dupe.absolute_path)
    print()
