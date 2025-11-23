import send2trash
import sys

from voussoirkit import pathclass
from voussoirkit import ffmpegtools
from voussoirkit import stringtools
from voussoirkit import timetools

if len(sys.argv) < 3:
    raise ValueError()

input_files = sys.argv[1:]
input_files = [pathclass.Path(p) for p in input_files]
input_files.sort(key=lambda f: stringtools.natural_sorter(f.normcase))
first_file = pathclass.Path(input_files[0])
output_file = first_file.parent.with_child(first_file.replace_extension('').basename + '_' + str(int(timetools.now().timestamp()))).add_extension(first_file.extension)

ffmpegtools.concatenate(input_files, output_file)

for file in input_files:
    send2trash.send2trash(file.absolute_path)
