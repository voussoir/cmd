import argparse
import re
import subprocess
import sys

from voussoirkit import pathclass
from voussoirkit import winglob
from voussoirkit import winwhich

AUDIO_EXTENSIONS = {
    'aac': 'm4a',
    'mp3': 'mp3',
    'opus': 'opus',
    '*': 'mka',
}

SUBTITLE_EXTENSIONS = {
    'ass': 'ass',
    'subrip': 'srt',
    '*': 'mks',
}

FFMPEG = winwhich.which('ffmpeg')

def ffextractor(input_filename, prefix, search_pattern, extension_map, moveto=None):
    input_filename = pathclass.Path(input_filename)

    if moveto is not None:
        moveto = pathclass.Path(moveto)

    command = [FFMPEG, '-i', input_filename.absolute_path]

    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as exc:
        output = exc.output
    output = output.decode('utf-8')

    maps = []
    for line in output.splitlines():
        match = re.search(search_pattern, line)
        if match is None:
            continue

        (stream_index, codec) = (match.group(1), match.group(2))
        extension = extension_map.get(codec, extension_map['*'])
        output_filename = input_filename.replace_extension('')
        output_filename = output_filename.add_extension(f'{prefix}{stream_index}.{extension}')

        if moveto:
            output_filename = moveto.with_child(output_filename.basename)

        args = ['-map', f'0:{stream_index}', '-c', 'copy']

        if extension == 'mks':
            args.extend(['-f', 'matroska'])

        args.append(output_filename.absolute_path)
        maps.extend(args)

    command = [FFMPEG, '-i', input_filename.absolute_path, *maps]
    print(command)
    subprocess.run(command, stderr=subprocess.STDOUT)

def ffaudios(input_filename, moveto=None):
    ffextractor(
        input_filename,
        prefix='a',
        search_pattern=r'Stream #0:(\d+)[^\s]*: Audio: (\w+)',
        extension_map=AUDIO_EXTENSIONS,
        moveto=moveto,
    )

def ffsubtitles(input_filename, moveto=None):
    ffextractor(
        input_filename,
        prefix='s',
        search_pattern=r'Stream #0:(\d+)[^\s]*: Subtitle: (\w+)',
        extension_map=SUBTITLE_EXTENSIONS,
        moveto=moveto,
    )

def ffstreams_argparse(args):
    for pattern in args.input_filename:
        for input_filename in winglob.glob(pattern):
            if args.audios:
                ffaudios(input_filename, moveto=args.moveto)
            if args.subtitles:
                ffsubtitles(input_filename, moveto=args.moveto)

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('input_filename', nargs='+')
    parser.add_argument('--moveto', dest='moveto', default=None)
    parser.add_argument('--audio', '--audios', dest='audios', action='store_true')
    parser.add_argument('--subtitles', '--subs', dest='subtitles', action='store_true')
    parser.set_defaults(func=ffstreams_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
