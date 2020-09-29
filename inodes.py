import sys

from voussoirkit import pathclass

def main(argv):
    for file in pathclass.cwd().listdir():
        if not file.is_file:
            continue
        print(file.stat.st_dev, file.stat.st_ino, file.relative_path)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
