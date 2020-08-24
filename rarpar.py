import argparse
import os
import re
import send2trash
import shutil
import sys
import time

from voussoirkit import betterhelp
from voussoirkit import bytestring
from voussoirkit import pathclass
from voussoirkit import winglob

RESERVE_SPACE_ON_DRIVE = 30 * bytestring.GIBIBYTE

class RarParException(Exception):
    pass

class NotEnoughSpace(RarParException):
    pass

def RARCOMMAND(
        path,
        basename,
        workdir,
        password=None,
        rec=None,
        rev=None,
        volume=None,
    ):
    '''
    winrar
        a = make archive
        -ibck = run in the background
        -ma = rar5 mode
        -m0 = compression level: store
        -mt1 = thread count: 1
        -v{x}M = split into x megabyte volumes
        -ri x:y = x priority (lower is less pri) y ms sleep between ops
        -r = include subdirectories
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
    command = [
        'winrar',
        'a -ibck -ma -m0 -mt1 -ri1:30 -r -ep1',
        '-y -xthumbs.db -xdesktop.ini',
    ]
    if volume is not None:
        command.append(f'-v{volume}M')

    if rec is not None:
        command.append(f'-rr{rec}%')

    if rev is not None:
        command.append(f'-rv{rev}%')

    if password is not None:
        command.append(f'-hp{password}')

    if path.is_dir:
        input_pattern = path.absolute_path + '\\*'
    else:
        input_pattern = path.absolute_path

    command.append(f'"{workdir.absolute_path}{os.sep}{basename}.rar"')
    command.append(f'"{input_pattern}"')

    command = ' '.join(command)
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
        'phpar2',
        'c -t1',
        f'-r{par}',
        f'"{workdir.absolute_path}{os.sep}{basename}"',
        f'"{workdir.absolute_path}{os.sep}{basename}*.rar"',
    ]
    command = ' '.join(command)
    return command

def assert_enough_space(pathsize, workdir, moveto, rec, rev, par):
    plus_percent = (rec + rev + par) / 100
    needed = pathsize * (1 + plus_percent)
    reserve = RESERVE_SPACE_ON_DRIVE + needed

    workdir_drive = os.path.splitdrive(workdir.absolute_path)[0]
    free_space = shutil.disk_usage(workdir_drive).free

    if moveto is not None:
        moveto_drive = os.path.splitdrive(moveto.absolute_path)[0]
        moveto_drive = pathclass.Path(moveto_drive)
        free_space = min(free_space, shutil.disk_usage(moveto_drive.absolute_path).free)

    message = ' '.join([
        f'For {bytestring.bytestring(pathsize)},',
        f'Reserving {bytestring.bytestring(reserve)} /',
        f'{bytestring.bytestring(free_space)}.',
    ])
    print(message)

    if reserve > free_space:
        raise NotEnoughSpace('Please leave more space')

def move(pattern, directory):
    files = winglob.glob(pattern)
    for file in files:
        print(file)
        shutil.move(file, directory)

def _normalize_percentage(rec):
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

def normalize_password(password):
    if password is None:
        return None

    if not isinstance(password, str):
        raise TypeError(f'password must be a {str}, not {type(password)}')

    if password == '':
        return None

    return password

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
            volume = (pathsize * volume) / bytestring.MIBIBYTE
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

    if dry:
        for command in script:
            print(command)
        return status

    for command in script:
        print(command)
        if isinstance(command, str):
            status = os.system(command)
        else:
            status = command()
        if status not in [0, None]:
            print('!!!! error status:', status)
            break

    return status

def rarpar(
        path,
        *,
        basename=None,
        dry=False,
        moveto=None,
        par=None,
        password=None,
        recycle_original=False,
        rec=None,
        rev=None,
        volume=None,
        workdir='.',
    ):
    path = pathclass.Path(path)

    path.assert_exists()

    workdir = pathclass.Path(workdir)
    workdir.assert_is_directory()

    if moveto:
        moveto = pathclass.Path(moveto)
        moveto.assert_is_directory()

    pathsize = path.size

    volume = normalize_volume(volume, pathsize)
    rec = _normalize_percentage(rec)
    rev = _normalize_percentage(rev)
    par = _normalize_percentage(par)

    if RESERVE_SPACE_ON_DRIVE:
        assert_enough_space(
            pathsize,
            workdir=workdir,
            moveto=moveto,
            rec=rec or 0,
            rev=rev or 0,
            par=par or 0,
        )

    timestamp = time.strftime('%Y-%m-%d')
    if not basename:
        basename = f'{path.basename} ({timestamp})'
    else:
        basename = basename.format(timestamp=timestamp)

    existing = winglob.glob(f'{basename}*.rar')
    if existing:
        raise Exception(f'{existing[0]} already exists.')

    #### ####

    script = []

    rarcommand = RARCOMMAND(
        path=path,
        basename=basename,
        password=password,
        rec=rec,
        rev=rev,
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

def rarpar_argparse(args):
    return rarpar(
        path=args.path,
        volume=args.volume,
        basename=args.basename,
        dry=args.dry,
        moveto=args.moveto,
        par=args.par,
        password=args.password,
        rec=args.rec,
        rev=args.rev,
        recycle_original=args.recycle_original,
        workdir=args.workdir,
    )

DOCSTRING = '''
path:
    The input file or directory to rarpar.

--volume X | X% | min(A, B) | max(A, B)
    Split rars into volumes of this many megabytes. Should be
    An integer number of megabytes, or;
    A percentage "X%" to calculate volumes as X% of the file size, down to
    a 1 MB minimum, or;
    A string "min(A, B)" or "max(A, B)" where A and B follow the above rules.

--rec X
    A integer to generate X% recovery record in the rars.
    See winrar documentation for information about recovery records.

--rev X
    A integer to generate X% recovery volumes.
    Note that winrar's behavior is the number of revs will always be less than
    the number of rars. If you don't split volumes, you will have 1 rar and
    thus 0 revs even if you ask for 100% rev.
    See winrar documentation for information about recovery volumes.

--par X
    A number to generate X% recovery with par2.

--basename
    A basename for the rar and par files. You will end up with
    basename.partXX.rar and basename.par2.
    Without this argument, the default basename is "basename ({timestamp})".
    Your string may include {timestamp} including the braces to get the
    timestamp there.

--password
    A password with which to encrypt the rar files.

--workdir:
    The directory in which the rars and pars will be generated while the
    program is working.

--moveto:
    The directory to which the rars and pars will be moved after the program
    has finished working.

--recycle:
    The input file or directory will be recycled at the end.

--dry:
    Print the commands that will be run, but don't actually run them.
'''

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('path')
    parser.add_argument('--volume', dest='volume')
    parser.add_argument('--rec', dest='rec')
    parser.add_argument('--rev', dest='rev')
    parser.add_argument('--par', dest='par')
    parser.add_argument('--basename', dest='basename')
    parser.add_argument('--password', dest='password')
    parser.add_argument('--workdir', dest='workdir', default='.')
    parser.add_argument('--moveto', dest='moveto')
    parser.add_argument('--recycle', dest='recycle_original', action='store_true')
    parser.add_argument('--dry', dest='dry', action='store_true')
    parser.set_defaults(func=rarpar_argparse)

    return betterhelp.single_main(argv, parser, DOCSTRING)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
