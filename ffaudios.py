import argparse
import re
import subprocess
import glob
import sys

from voussoirkit import pathclass
from voussoirkit import winwhich

EXTENSIONS = {
    'aac': 'm4a',
    'mp3': 'mp3',
    'opus': 'opus',
}

ffmpeg = winwhich.which('ffmpeg')

def ffaudios(input_filename, moveto=None):
    input_filename = pathclass.Path(input_filename)
    if moveto is not None:
        moveto = pathclass.Path(moveto)
    command = [ffmpeg, '-i', input_filename.absolute_path]

    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as exc:
        output = exc.output

    output = output.decode('utf-8')
    maps = []
    for line in output.splitlines():
        match = re.search(r'Stream #0:(\d+)[^\s]*: Audio: (\w+)', line)
        if match is None:
            continue
        (stream_index, codec) = (match.group(1), match.group(2))
        extension = EXTENSIONS.get(codec, 'mka')
        output_filename = input_filename.replace_extension('').add_extension(f'{stream_index}.{extension}')
        if moveto:
            output_filename = moveto.with_child(output_filename.basename)
        maps.extend(['-map', f'0:{stream_index}', '-c', 'copy', output_filename.absolute_path])
        # print(output_filename)

    command = [ffmpeg, '-i', input_filename.absolute_path, *maps]
    print(command)
    subprocess.run(command, stderr=subprocess.STDOUT)


def ffaudios_argparse(args):
    for pattern in args.input_filename:
        for input_filename in glob.glob(pattern):
            ffaudios(input_filename, moveto=args.moveto)

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('input_filename', nargs='+')
    parser.add_argument('--moveto', dest='moveto', default=None)
    parser.set_defaults(func=ffaudios_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
