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

# Here is an example of typical git status output:
#
# On branch master
# Changes not staged for commit:
#   (use "git add/rm <file>..." to update what will be committed)
#   (use "git checkout -- <file>..." to discard changes in working directory)
#
#         modified:   file1
#         deleted:    file2
#
# Untracked files:
#   (use "git add <file>..." to include in what will be committed)
#
#         file3
#
# no changes added to commit (use "git add" and/or "git commit -a")
# --- ALTERNATE LAST LINE ---
# nothing added to commit but untracked files present (use "git add" to track)

# Here is an example of typical git log -1 --decorate output:
#
# commit f8fddd0de4283a251a8beb35493bd1bd3a4c925a (HEAD -> master)
# Author: My Name <mymail@example.net>
# Date:   Sat Jan 11 01:59:07 2020 -0800
#
#     I made some changes.

def checkup_committed(directory):
    os.chdir(directory)
    command = [GIT, 'status']
    output = subprocess.check_output(command, stderr=subprocess.STDOUT)

    if b'nothing to commit' in output:
        committed = True
        details = ''

    else:
        committed = False

        if b'Untracked files' in output:
            added = output.split(b'include in what will be committed)')[1]
            added = added.split(b'no changes added to commit')[0]
            added = added.split(b'nothing added to commit but')[0]
            added = [x.strip() for x in added.splitlines()]
            added = [x for x in added if x]
            added = len(added)
        else:
            added = 0

        modified = output.count(b'modified:')
        deleted = output.count(b'deleted:')
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
