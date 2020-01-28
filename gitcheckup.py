import argparse
import os
import subprocess
import sys

from voussoirkit import winwhich

GIT = winwhich.which('git')

# https://git-scm.com/docs/git-status#_short_format
# Here is an example of typical `git status --short` output:
#
#  M file1
#  D file2
# A  file4
# ?? file3

def checkup_committed():
    command = [GIT, 'status', '--short', '--untracked-files=all']
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
        details = []
        if added: details.append(f'+{added}')
        if deleted: details.append(f'-{deleted}')
        if modified: details.append(f'~{modified}')
        details = ', '.join(details)
        details = f'({details})'

    return (committed, details)

def checkup_pushed():
    command = [GIT, 'rev-parse', '@']
    my_head = subprocess.check_output(command, stderr=subprocess.STDOUT)
    my_head = my_head.strip().decode()

    command = [GIT, 'rev-parse', '@{u}']
    remote_head = subprocess.check_output(command, stderr=subprocess.STDOUT)
    remote_head = remote_head.strip().decode()

    command = [GIT, 'merge-base', '@', '@{u}']
    merge_base = subprocess.check_output(command, stderr=subprocess.STDOUT)
    merge_base = merge_base.strip().decode()

    if my_head == remote_head:
        to_push = 0
        to_pull = 0
    else:
        to_push = len(git_commits_between(merge_base, my_head))
        to_pull = len(git_commits_between(merge_base, remote_head))

    if (to_push, to_pull) == (0, 0):
        pushed = True
        details = ''
    else:
        pushed = False
        details = []
        if to_push: details.append(f'↑{to_push}')
        if to_pull: details.append(f'↓{to_pull}')
        details = ', '.join(details)
        details = f'({details})'

    return (pushed, details)

def git_commits_between(a, b):
    command = [GIT, 'log', '--oneline', f'{a}..{b}']
    output = subprocess.check_output(command, stderr=subprocess.STDOUT)
    lines = output.strip().decode().splitlines()
    return lines

def git_fetch():
    command = [GIT, 'fetch', '--all']
    output = subprocess.check_output(command, stderr=subprocess.STDOUT)

def checkup(directory, do_fetch=False):
    os.chdir(directory)
    if do_fetch:
        git_fetch()
    (committed, commit_details) = checkup_committed()
    (pushed, push_details) = checkup_pushed()
    return {
        'committed': committed,
        'commit_details': commit_details,
        'pushed': pushed,
        'push_details': push_details,
    }

def gitcheckup(do_fetch=False):
    directories_file = os.path.join(os.path.dirname(__file__), 'gitcheckup.txt')
    try:
        handle = open(directories_file, 'r')
    except FileNotFoundError:
        print(f'Please put your git repo locations in {directories_file}.')
        return 1

    directories = handle.readlines()
    handle.close()

    directories = [line.strip() for line in directories]
    directories = [line for line in directories if line]

    for directory in directories:
        result = checkup(directory, do_fetch=do_fetch)
        committed = 'C' if result['committed'] else ' '
        pushed = 'P' if result['pushed'] else ' '

        details = []
        if result['commit_details']:
            details.append(result['commit_details'])
        if result['push_details']:
            details.append(result['push_details'])
        details = ' '.join(details)
        details = (' ' + details).rstrip()
        print(f'[{committed}][{pushed}] {directory}{details}')

def gitcheckup_argparse(args):
    return gitcheckup(do_fetch=args.do_fetch)

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('--fetch', dest='do_fetch', action='store_true')
    parser.set_defaults(func=gitcheckup_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
