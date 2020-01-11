import os
import subprocess
import sys

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

# https://git-scm.com/docs/git-status#_short_format
# Here is an example of typical `git status --short` output:
#
#  M file1
#  D file2
# A  file4
# ?? file3

# Here is an example of typical `git log -1 --decorate` output:
#
# commit f8fddd0de4283a251a8beb35493bd1bd3a4c925a (HEAD -> master)
# Author: My Name <mymail@example.net>
# Date:   Sat Jan 11 01:59:07 2020 -0800
#
#     I made some changes.

def checkup_committed(directory):
    os.chdir(directory)
    command = [GIT, 'status', '--short']
    output = subprocess.check_output(command, stderr=subprocess.STDOUT)

    added = 0
    modified = 0
    deleted = 0
    for line in output.splitlines():
        status = line.split()[0].strip().decode('ascii')

        # These are ifs instead of elifs because you might have a file that is
        # added in the index but deleted on disk, etc. Anyway these numbers
        # don't need to be super accurate, just enough to remind you to commit.
        if {'A', '?'}.intersection(status):
            added += 1
        if {'M', 'R', '!'}.intersection(status):
            modified += 1
        if {'D'}.intersection(status):
            deleted += 1

    if (added, modified, deleted) == (0, 0, 0):
        committed = True
        details = ''
    else:
        committed = False
        details = f'+{added}, -{deleted}, ~{modified}'

    return (committed, details)

def checkup_pushed(directory):
    os.chdir(directory)
    command = [GIT, 'log', '-1', '--decorate']
    output = subprocess.check_output(command, stderr=subprocess.STDOUT)
    headline = output.splitlines()[0]
    refs = headline.split(b'(')[-1].split(b')')[0]
    return any (b'/' in ref for ref in refs.split(b','))

def checkup(directory):
    (committed, details) = checkup_committed(directory)
    pushed = checkup_pushed(directory)
    return {'committed': committed, 'pushed': pushed, 'details': details}

def main(argv):
    for directory in DIRECTORIES:
        result = checkup(directory)
        committed = 'C' if result['committed'] else ' '
        pushed = 'P' if result['pushed'] else ' '
        details = result['details']
        details = f' ({details})' if details else ''
        print(f'[{committed}][{pushed}] {directory}{details}')

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
