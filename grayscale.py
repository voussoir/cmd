import PIL.Image
import sys

from voussoirkit import pathclass
from voussoirkit import pipeable
from voussoirkit import winglob

def main(argv):
    for pattern in pipeable.go(argv, strip=True, skip_blank=True):
        filenames = winglob.glob(pattern)
        for filename in filenames:
            filename = pathclass.Path(filename)
            if filename.replace_extension('').basename.endswith('_gray'):
                continue
            new_filename = filename.replace_extension('').absolute_path + '_gray' + filename.dot_extension
            print(f'{filename.basename} -> {new_filename.basename}')
            image = PIL.Image.open(filename.absolute_path).convert('LA')
            image.save(new_filename)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
