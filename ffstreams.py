import argparse
import re
import subprocess
import sys

from voussoirkit import pathclass
from voussoirkit import winglob
from voussoirkit import winwhich
from voussoirkit import vlogging

log = vlogging.getLogger(__name__, 'ffstreams')

AUDIO_EXTENSIONS = {
    'aac': 'm4a',
    'ac3': 'ac3',
    'flac': 'flac',
    'mp3': 'mp3',
    'opus': 'opus',
    'vorbis': 'ogg',
    '*': 'mka',
}

SUBTITLE_EXTENSIONS = {
    'ass': 'ass',
    'subrip': 'srt',
    '*': 'mks',
}

FFMPEG = winwhich.which('ffmpeg')

def make_maps(input_file, prefix, search_pattern, extension_map, moveto=None):
    input_file = pathclass.Path(input_file)

    if moveto is not None:
        moveto = pathclass.Path(moveto)

    command = [FFMPEG, '-i', input_file.absolute_path]

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

        (stream_index, language, codec) = match.groups()
        if language is None:
            language = ''
        else:
            language = language.strip('()')
            language = '.' + language
        extension = extension_map.get(codec, extension_map['*'])
        output_filename = input_file.replace_extension('')
        output_filename = output_filename.add_extension(f'{prefix}{stream_index}{language}.{extension}')
        log.debug(f'{stream_index}, codec={codec}, ext=.{extension}')

        if moveto:
            output_filename = moveto.with_child(output_filename.basename)

        args = ['-map', f'0:{stream_index}', '-c', 'copy']

        if extension == 'mks':
            args.extend(['-f', 'matroska'])

        args.append(output_filename.absolute_path)
        maps.extend(args)
    return maps

def video_maps(input_file, moveto=None):
    return make_maps(
        input_file,
        prefix='v',
        search_pattern=r'Stream #0:(\d+)(\(\w+\))?[^\s]*: Video: (\w+)',
        extension_map=AUDIO_EXTENSIONS,
        moveto=moveto,
    )

def audio_maps(input_file, moveto=None):
    return make_maps(
        input_file,
        prefix='a',
        search_pattern=r'Stream #0:(\d+)(\(\w+\))?[^\s]*: Audio: (\w+)',
        extension_map=AUDIO_EXTENSIONS,
        moveto=moveto,
    )

def subtitle_maps(input_file, moveto=None):
    return make_maps(
        input_file,
        prefix='s',
        search_pattern=r'Stream #0:(\d+)(\(\w+\))?[^\s]*: Subtitle: (\w+)',
        extension_map=SUBTITLE_EXTENSIONS,
        moveto=moveto,
    )

def ffstreams(
        input_file,
        do_videos=False,
        do_audios=False,
        do_subtitles=False,
        dry=False,
        moveto=None,
    ):
    maps = []
    if do_videos:
        maps.extend(video_maps(input_file, moveto=moveto))

    if do_audios:
        maps.extend(audio_maps(input_file, moveto=moveto))

    if do_subtitles:
        maps.extend(subtitle_maps(input_file, moveto=moveto))

    if not maps:
        return

    command = [FFMPEG, '-i', input_file.absolute_path, *maps]

    log.info(command)
    if not dry:
        subprocess.run(command, stderr=subprocess.STDOUT)

def ffstreams_argparse(args):
    for pattern in args.input_filename:
        for input_filename in winglob.glob(pattern):
            input_file = pathclass.Path(input_filename)
            ffstreams(
                input_file,
                do_videos=args.videos,
                do_audios=args.audios,
                do_subtitles=args.subtitles,
                dry=args.dry,
                moveto=args.moveto,
            )

    return 0

@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input_filename', nargs='+')
    parser.add_argument('--moveto', default=None)
    parser.add_argument('--video', '--videos', dest='videos', action='store_true')
    parser.add_argument('--audio', '--audios', dest='audios', action='store_true')
    parser.add_argument('--subtitles', '--subs', dest='subtitles', action='store_true')
    parser.add_argument('--dry', dest='dry', action='store_true')
    parser.set_defaults(func=ffstreams_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
