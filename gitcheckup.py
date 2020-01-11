import sys
import subprocess
import os

from voussoirkit import winwhich

GIT = winwhich.which('git')

DIRECTORIES = [
    r'D:\Git\cmd',
    r'D:\Git\epubfile',
    r'D:\Git\Etiquette',
    r'D:\Git\reddit',
    r'D:\Git\reddit\Timesearch',
    r'D:\Git\sigilplugins',
    r'D:\Git\voussoirkit',
    r'D:\Git\YCDL',
]

def checkup(directory):
    os.chdir(directory)
    command = [GIT, 'status']
    output = subprocess.check_output(command, stderr=subprocess.STDOUT)
    if b'nothing to commit' in output:
        committed = True
        details = ''
    else:
        modified = output.count(b'modified:')
        deleted = output.count(b'deleted:')

        if b'Untracked files' in output:
            added = output.split(b'in what will be committed)')[1]
            added = added.split(b'no changes added to commit')[0]
            added = added.split(b'nothing added to commit but')[0]
            added = [x.strip() for x in added.splitlines()]
            added = [x for x in added if x]
            added = len(added)
        else:
            added = 0

        committed = False
        details = f'(+{added}, -{deleted}, ~{modified})'

    command = [GIT, 'log', '-1', '--decorate']
    output = subprocess.check_output(command, stderr=subprocess.STDOUT)
    headline = output.splitlines()[0]
    locations = headline.split(b'(')[-1].split(b')')[0]
    if b',' in locations:
        pushed = True
    else:
        pushed = False
    return {'committed': committed, 'pushed': pushed, 'details': details}

def checkup_all():
    print('[C][P]')
    for directory in DIRECTORIES:
        result = checkup(directory)
        committed = 'x' if result['committed'] else ' '
        pushed = 'x' if result['pushed'] else ' '
        details = (' ' + result['details']) if result['details'] else ''
        print(f'[{committed}][{pushed}] {directory}{details}')

def main(argv):
    checkup_all()

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
