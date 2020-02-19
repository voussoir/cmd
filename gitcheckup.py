import argparse
import os
import subprocess
import sys
import types

from voussoirkit import dotdict
from voussoirkit import winwhich

GIT = winwhich.which('git')

# https://git-scm.com/docs/git-status#_short_format
# Here is an example of typical `git status --short` output:
#
#  M file1
#  D file2
# A  file4
# ?? file3

class GitCheckupException(Exception):
    pass

class NoConfigFile(GitCheckupException):
    def __str__(self):
        return f'Please put your git repo locations in "{self.args[0]}".'

class NoUpstreamBranch(GitCheckupException):
    def __str__(self):
        return f'No upstream branch for {self.args[0]}.'

# HELPERS
################################################################################
def check_output(command):
    output = subprocess.check_output(command, stderr=subprocess.STDOUT)
    return output

def read_directories_file():
    directories_file = os.path.join(os.path.dirname(__file__), 'gitcheckup.txt')

    try:
        handle = open(directories_file, 'r')
    except FileNotFoundError as exc:
        raise NoConfigFile(exc.filename) from exc

    with handle:
        directories = handle.readlines()

    directories = [line.strip() for line in directories]
    directories = [line for line in directories if line]

    return directories

# GIT FUNCTIONS
################################################################################
def git_commits_between(a, b):
    command = [GIT, 'log', '--oneline', f'{a}..{b}']
    output = check_output(command)
    lines = output.strip().decode().splitlines()
    return lines

def git_fetch():
    command = [GIT, 'fetch', '--all']
    output = check_output(command)

# CHECKUP
################################################################################
def checkup_committed():
    details = dotdict.DotDict(default=None)

    command = [GIT, 'status', '--short', '--untracked-files=all']
    output = check_output(command)

    details.added = 0
    details.modified = 0
    details.deleted = 0
    for line in output.splitlines():
        status = line.split()[0].strip().decode('ascii')

        # These are ifs instead of elifs because you might have a file that is
        # added in the index but deleted on disk, etc. Anyway these numbers
        # don't need to be super accurate, just enough to remind you to commit.
        if {'A', '?'}.intersection(status):
            details.added += 1
        if {'M', 'R', '!'}.intersection(status):
            details.modified += 1
        if {'D'}.intersection(status):
            details.deleted += 1

    details.committed = (details.added, details.modified, details.deleted) == (0, 0, 0)

    return details

def checkup_pushed():
    details = dotdict.DotDict(default=None)

    command = [GIT, 'rev-parse', '@']
    my_head = check_output(command).strip().decode()

    command = [GIT, 'rev-parse', '@{u}']
    try:
        remote_head = check_output(command).strip().decode()
    except subprocess.CalledProcessError as exc:
        command = [GIT, 'rev-parse', '--abbrev-ref', 'HEAD']
        current_branch = check_output(command).strip().decode()
        details.error = NoUpstreamBranch(current_branch)
        return details

    if my_head == remote_head:
        details.to_push = 0
        details.to_pull = 0
    else:
        command = [GIT, 'merge-base', '@', '@{u}']
        merge_base = check_output(command).strip().decode()

        if my_head == merge_base:
            details.to_push = 0
            details.to_pull = len(git_commits_between(merge_base, remote_head))
        elif remote_head == merge_base:
            details.to_push = len(git_commits_between(merge_base, my_head))
            details.to_pull = 0
        else:
            details.to_push = len(git_commits_between(merge_base, my_head))
            details.to_pull = len(git_commits_between(merge_base, remote_head))

    details.pushed = (details.to_push, details.to_pull) == (0, 0)
    return details

def gitcheckup(directory, do_fetch=False):
    directory = os.path.abspath(directory)
    os.chdir(directory)

    if do_fetch:
        git_fetch()

    try:
        commit_details = checkup_committed()
        push_details = checkup_pushed()
    except subprocess.CalledProcessError as exc:
        raise Exception(exc.output)

    committed = 'C' if commit_details.committed else ' '
    pushed = 'P' if push_details.pushed else ' '

    details = []

    commit_summary = []
    if commit_details.added: commit_summary.append(f'+{commit_details.added}')
    if commit_details.deleted: commit_summary.append(f'-{commit_details.deleted}')
    if commit_details.modified: commit_summary.append(f'~{commit_details.modified}')
    commit_summary = ', '.join(commit_summary)
    if commit_summary: details.append(f'({commit_summary})')

    push_summary = []
    if push_details.to_push: push_summary.append(f'↑{push_details.to_push}')
    if push_details.to_pull: push_summary.append(f'↓{push_details.to_pull}')
    if push_details.error: push_summary.append(f'!{push_details.error}')
    push_summary = ', '.join(push_summary)
    if push_summary: details.append(f'({push_summary})')

    details = ' '.join(details)
    details = (' ' + details).rstrip()
    print(f'[{committed}][{pushed}] {directory}{details}')

# COMMAND LINE
################################################################################
def gitcheckup_argparse(args):
    if args.directories:
        directories = args.directories
    else:
        directories = read_directories_file()

    for directory in directories:
        gitcheckup(directory, do_fetch=args.do_fetch)

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('directories', nargs='*')
    parser.add_argument('--fetch', dest='do_fetch', action='store_true')
    parser.set_defaults(func=gitcheckup_argparse)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except GitCheckupException as exc:
        print(exc)
        return 1

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
