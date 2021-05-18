import collections

from voussoirkit import spinal

counts = collections.Counter()
extensions = {}
walker = spinal.walk()
for file in walker:
    extensions.setdefault(file.extension, []).append(file)
    counts[file.extension] += 1

for (extension, count) in counts.most_common():
    files = extensions[extension]
    print(f'{extension.with_dot}: {len(files)}')
    if len(files) < 5:
        for file in files:
            print(f'    {file.absolute_path}')
