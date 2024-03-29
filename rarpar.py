import argparse
import os
import re
import send2trash
import shutil
import subprocess
import sys
import time

from voussoirkit import betterhelp
from voussoirkit import bytestring
from voussoirkit import operatornotify
from voussoirkit import pathclass
from voussoirkit import subproctools
from voussoirkit import vlogging
from voussoirkit import winglob
from voussoirkit import winwhich

log = vlogging.getLogger(__name__, 'rarpar')

WINRAR = winwhich.which('winrar')
PAR2 = winwhich.which('phpar2')

RESERVE_SPACE_ON_DRIVE = 5 * bytestring.GIBIBYTE

COMPRESSION_STORE = 0
COMPRESSION_MAX = 5

class RarParException(Exception):
    pass

class RarExists(RarParException):
    pass

class NotEnoughSpace(RarParException):
    pass

def RARCOMMAND(
        path,
        basename,
        workdir,
        compression=None,
        dictionary_size=None,
        password=None,
        profile=None,
        rec=None,
        rev=None,
        solid=False,
        volume=None,
    ):
    '''
    winrar
        a = make archive
        -cp{profile} = use compression profile. this must come first so that
                       all subsequent options override the ones provided by
                       the profile.
        -ibck = run in the background
        -dh = allow winrar to read files which are in use by another process.
              Without this flag, winrar exits with status 6 in that case.
        -ma = rar5 mode
        -m{compression} = 0: store, 5: max
        -md{x}[kmg] = x kilobytes/megabytes/gigabytes dictionary size
        -mt1 = thread count: 1
        -v{x}M = split into x megabyte volumes
        -ri x:y = x priority (lower is less pri) y ms sleep between ops
        -r = include subdirectories
        -s = solid
        -ep1 = arcnames will start relative to the main folder,
               instead of having the whole abspath of the input_pattern.
        -rr{x}% = x% recovery record
        -rv{x}% = x% recovery volumes
        -hp{x} = encrypt with password x
        -y = yes on all prompts
        -x = exclude certain filenames
    destination
        workdir/basename.rar
    files to include
        input_pattern
    '''
    command = [WINRAR, 'a']

    if profile is not None:
        command.append(f'-cp{profile}')

    command.extend([
        '-ibck',
        '-dh',
        '-ma',
        '-mt1',
        '-ri1:30',
        '-ep1',
        '-y',
        '-xthumbs.db',
        '-xdesktop.ini',
    ])

    if compression is not None:
        command.append(f'-m{compression}')

    if dictionary_size is not None:
        command.append(f'-md{dictionary_size}')

    if solid:
        command.append('-s')

    if volume is not None:
        command.append(f'-v{volume}M')

    if rec is not None:
        command.append(f'-rr{rec}%')

    if rev is not None:
        command.append(f'-rv{rev}%')

    if password is not None:
        command.append(f'-hp{password}')

    if path.is_dir:
        command.append('-r')

    input_pattern = path.absolute_path

    command.append(workdir.with_child(f'{basename}.rar').absolute_path)
    command.append(f'{input_pattern}')

    return command

def PARCOMMAND(workdir, basename, par):
    '''
    phpar2
        c = create pars
        -t1 = thread count: 1
        -r{x} = x% recovery
    destination
        workdir/basename.par2
    '''
    command = [
        PAR2,
        'c', '-t1',
        f'-r{par}',
        '--',
        workdir.with_child(f'{basename}').absolute_path,
        workdir.with_child(f'{basename}*.rar').absolute_path,
    ]
    return command

def assert_enough_space(path, size, rec, rev, par):
    plus_percent = (rec + rev + par) / 100
    needed = size * (1 + plus_percent)
    reserve = RESERVE_SPACE_ON_DRIVE + needed
    reserve = int(reserve)

    path.assert_disk_space(reserve)

def move(pattern, directory):
    files = winglob.glob(pattern)
    for file in files:
        print(file)
        shutil.move(file, directory)

def normalize_compression(compression):
    if compression is None:
        return None

    if isinstance(compression, str):
        compression = compression.lower()
        if compression == 'max':
            return COMPRESSION_MAX
        elif compression == 'store':
            return COMPRESSION_STORE
        else:
            compression = int(compression)

    if isinstance(compression, int):
        if compression < COMPRESSION_STORE or compression > COMPRESSION_MAX:
            raise ValueError(f'Compression level {compression} is invalid.')
        return compression

    raise TypeError(f'Compression should be an integer or max or store, not {type(compression)}.')

def normalize_dictionary_size(dictionary):
    if dictionary is None:
        return None

    dictionary = dictionary.strip().lower()

    if not re.match(r'^\d+(k|m|g)?$', dictionary):
        raise ValueError(f'dictionary_size {dictionary} is invalid.')

    if re.match(r'^\d+$', dictionary):
        dictionary += 'm'

    # https://www.winrar-france.fr/winrar_instructions_for_use/source/html/HELPSwMD.htm
    VALID = [
        '128k',
        '256k',
        '512k',
        '1m',
        '2m',
        '4m',
        '8m',
        '16m',
        '32m',
        '64m',
        '128m',
        '256m',
        '512m',
        '1g',
    ]

    if dictionary not in VALID:
        raise ValueError(f'dictionary_size {dictionary} is invalid.')

    return dictionary

def normalize_password(password):
    if password is None:
        return None

    if not isinstance(password, str):
        raise TypeError(f'password must be a {str}, not {type(password)}')

    if password == '':
        return None

    return password

def normalize_percentage(rec):
    if rec is None:
        return None

    if rec == 0:
        return None

    if isinstance(rec, str):
        rec = rec.strip('%')

    rec = int(rec)

    if not (0 <= rec <= 100):
        raise ValueError(f'rec, rev, par {rec} must be 0-100.')

    return rec

def _normalize_volume(volume, pathsize):
    if volume is None:
        return None

    if isinstance(volume, int):
        return volume

    if isinstance(volume, float):
        return int(volume)

    if isinstance(volume, str):
        volume = volume.strip()

        if volume == '100%':
            return None

        minmax_parts = re.findall(r'(min|max)\((.+?), (.+?)\)', volume)
        if minmax_parts:
            (func, left, right) = minmax_parts[0]
            func = {'min': min, 'max': max}[func]
            left = _normalize_volume(left, pathsize=pathsize)
            right = _normalize_volume(right, pathsize=pathsize)
            return func(left, right)

        if volume.endswith('%'):
            volume = volume[:-1]
            volume = float(volume) / 100
            volume = (pathsize * volume) / bytestring.MEBIBYTE
            volume = max(1, volume)
            return int(volume)

        return int(volume)

    raise TypeError(f'Invalid volume {type(volume)}.')

def normalize_volume(volume, pathsize):
    volume = _normalize_volume(volume, pathsize)
    if volume is not None and volume < 1:
        raise ValueError('Volume must be >= 1.')
    return volume

def run_script(script, dry=False):
    '''
    `script` can be a list of strings, which are command line commands, or
    callable Python functions. They will be run in order, and the sequence
    will terminate if any step returns a bad status code. Your Python functions
    must return either 0 or None to be considered successful, all other return
    values will be considered failures.
    '''
    status = 0

    for command in script:
        if isinstance(command, str):
            log.info(command)
        elif isinstance(command, list):
            log.info(subproctools.format_command(command))
        else:
            log.info(command)

        if dry:
            continue

        if isinstance(command, str):
            status = os.system(command)
        elif isinstance(command, list):
            # sys.stdout is None indicates pythonw.
            creationflags = subprocess.CREATE_NO_WINDOW if sys.stdout is None else 0
            status = subprocess.run(command, creationflags=creationflags).returncode
        else:
            status = command()
        if status not in [0, None]:
            log.error('!!!! error status: %s', status)
            break

    return status

def rarpar(
        path,
        *,
        basename=None,
        compression=None,
        dictionary_size=None,
        dry=False,
        moveto=None,
        par=None,
        password=None,
        rar_profile=None,
        recycle_original=False,
        rec=None,
        rev=None,
        solid=False,
        volume=None,
        workdir='.',
    ):
    path = pathclass.Path(path)

    # Validation ###################################################################################

    path.assert_exists()
    path.correct_case()

    workdir = pathclass.Path(workdir)
    workdir.assert_is_directory()

    if moveto is not None:
        moveto = pathclass.Path(moveto)
        moveto.assert_is_directory()

    compression = normalize_compression(compression)

    dictionary_size = normalize_dictionary_size(dictionary_size)

    if type(solid) is not bool:
        raise TypeError(f'solid must be True or False, not {solid}.')

    password = normalize_password(password)

    pathsize = path.size
    volume = normalize_volume(volume, pathsize)
    rec = normalize_percentage(rec)
    rev = normalize_percentage(rev)
    par = normalize_percentage(par)

    if RESERVE_SPACE_ON_DRIVE:
        assert_enough_space(
            path=workdir,
            size=pathsize,
            rec=rec or 0,
            rev=rev or 0,
            par=par or 0,
        )
    if RESERVE_SPACE_ON_DRIVE and moveto is not None:
        assert_enough_space(
            path=moveto,
            size=pathsize,
            rec=rec or 0,
            rev=rev or 0,
            par=par or 0,
        )

    date = time.strftime('%Y-%m-%d')
    timestamp = time.strftime('%Y-%m-%d_%H-%M-%S')

    if basename is not None:
        basename = re.sub(r'\.rar$', '', basename)

    if not basename:
        basename = f'{path.basename} ({timestamp})'
    else:
        basename = basename.format(basename=path.basename, date=date, timestamp=timestamp)

    existing = None
    if workdir:
        existing = existing or workdir.glob(f'{basename}*.rar')
    if moveto:
        existing = existing or moveto.glob(f'{basename}*.rar')

    if existing:
        raise RarExists(f'{existing[0].absolute_path} already exists.')

    # Script building ##############################################################################

    script = []

    rarcommand = RARCOMMAND(
        path=path,
        basename=basename,
        compression=compression,
        dictionary_size=dictionary_size,
        password=password,
        profile=rar_profile,
        rec=rec,
        rev=rev,
        solid=solid,
        volume=volume,
        workdir=workdir,
    )
    script.append(rarcommand)

    if par:
        parcommand = PARCOMMAND(
            basename=basename,
            par=par,
            workdir=workdir,
        )
        script.append(parcommand)

    def move_rars():
        move(f'{workdir.absolute_path}\\{basename}*.rar', f'{moveto.absolute_path}')

    def move_revs():
        move(f'{workdir.absolute_path}\\{basename}*.rev', f'{moveto.absolute_path}')

    def move_pars():
        move(f'{workdir.absolute_path}\\{basename}*.par2', f'{moveto.absolute_path}')

    if moveto:
        if True:
            script.append(move_rars)
        if rev:
            script.append(move_revs)
        if par:
            script.append(move_pars)

    def recycle():
        send2trash.send2trash(path.absolute_path)

    if recycle_original:
        script.append(recycle)

    #### ####

    status = run_script(script, dry)

    return status

# COMMAND LINE #####################################################################################

def rarpar_argparse(args):
    status = 0
    try:
        return rarpar(
            path=args.path,
            volume=args.volume,
            basename=args.basename,
            compression=args.compression,
            dictionary_size=args.dictionary_size,
            dry=args.dry,
            moveto=args.moveto,
            par=args.par,
            password=args.password,
            rar_profile=args.rar_profile,
            rec=args.rec,
            rev=args.rev,
            recycle_original=args.recycle_original,
            solid=args.solid,
            workdir=args.workdir,
        )
    except (RarExists, pathclass.NotEnoughSpace) as exc:
        log.fatal(exc)
        status = 1

    return status

@operatornotify.main_decorator(subject='rarpar.py')
@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        'path',
        type=pathclass.Path,
        help='''
        The input file or directory to rarpar.
        ''',
    )
    parser.add_argument(
        '--volume',
        help='''
        Split rars into volumes of this many megabytes. Should be:
        - An integer number of megabytes, or
        - A percentage "X%" to calculate volumes as X% of the file size, down to
          a 1 MB minimum, or
        - A string "min(A, B)" or "max(A, B)" where A and B follow the above rules.
        ''',
    )
    parser.add_argument(
        '--rec',
        type=int,
        help='''
        An integer to generate X% recovery record in the rars.
        See winrar documentation for information about recovery records.
        ''',
    )
    parser.add_argument(
        '--rev',
        type=int,
        help='''
        An integer to generate X% recovery volumes.
        Note that winrar's behavior is the number of revs will always be less than
        the number of rars. If you don't split volumes, you will have 1 rar and
        thus 0 revs even if you ask for 100% rev.
        See winrar documentation for information about recovery volumes.
        ''',
    )
    parser.add_argument(
        '--par',
        type=int,
        help='''
        A number to generate X% recovery with par2.
        ''',
    )
    parser.add_argument(
        '--basename',
        type=str,
        help='''
        A basename for the rar and par files. You will end up with
        basename.partXX.rar and basename.par2.
        Without this argument, the default basename is "{basename} ({timestamp})".
        Your string may include {basename}, {timestamp} and/or {date} including the
        braces to insert that value there.
        ''',
    )
    parser.add_argument(
        '--compression',
        help='''
        Level of compression. Can be "store" or "max" or integer 0-5.
        ''',
    )
    parser.add_argument(
        '--password',
        type=str,
        help='''
        A password with which to encrypt the rar files.
        ''',
    )
    parser.add_argument(
        '--profile', dest='rar_profile',
    )
    parser.add_argument(
        '--workdir',
        type=pathclass.Path,
        default='.',
        help='''
        The directory in which the rars and pars will be generated while the
        program is working.
        ''',
    )
    parser.add_argument(
        '--moveto',
        type=pathclass.Path,
        help='''
        The directory to which the rars and pars will be moved after the program
        has finished working.
        ''',
    )
    parser.add_argument(
        '--recycle',
        dest='recycle_original',
        action='store_true',
        help='''
        The input file or directory will be recycled at the end.
        ''',
    )
    parser.add_argument(
        '--dictionary',
        dest='dictionary_size',
        help='''
        Larger dictionary sizes can improve compression in exchange for higher
        memory usage. Accepted values are 128k, 256k, 512k, 1m, 2m, 4m, 8m, 16m,
        32m, 64m, 128m, 256m, 512m, 1g.
        '''
    )
    parser.add_argument(
        '--solid',
        action='store_true',
        help='''
        Generate a 'solid' rar archive. See winrar's documentation for details.
        ''',
    )
    parser.add_argument(
        '--dry',
        action='store_true',
        help='''
        Print the commands that will be run, but don't actually run them.
        ''',
    )
    parser.set_defaults(func=rarpar_argparse)

    return betterhelp.go(parser, argv)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
