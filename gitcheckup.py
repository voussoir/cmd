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

class NoUpstreamBranch(Exception):
    def __str__(self):
        return f'No upstream branch for {self.args[0]}'

def check_output(command):
    output = subprocess.check_output(command, stderr=subprocess.STDOUT)
    return output

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

def git_commits_between(a, b):
    command = [GIT, 'log', '--oneline', f'{a}..{b}']
    output = check_output(command)
    lines = output.strip().decode().splitlines()
    return lines

def git_fetch():
    command = [GIT, 'fetch', '--all']
    output = check_output(command)

def checkup(directory, do_fetch=False):
    os.chdir(directory)
    if do_fetch:
        git_fetch()
    commit_details = checkup_committed()
    push_details = checkup_pushed()
    return dotdict.DotDict(
        commit_details=commit_details,
        push_details=push_details,
    )

def read_directories_file():
    directories_file = os.path.join(os.path.dirname(__file__), 'gitcheckup.txt')

    handle = open(directories_file, 'r')
    directories = handle.readlines()
    handle.close()

    directories = [line.strip() for line in directories]
    directories = [line for line in directories if line]

    return directories

def gitcheckup_one(directory, do_fetch=False):
    try:
        result = checkup(directory, do_fetch=do_fetch)
    except subprocess.CalledProcessError as exc:
        raise Exception(exc.output)

    committed = 'C' if result.commit_details.committed else ' '
    pushed = 'P' if result.push_details.pushed else ' '

    details = []

    commit_details = []
    if result.commit_details.added: commit_details.append(f'+{result.commit_details.added}')
    if result.commit_details.deleted: commit_details.append(f'-{result.commit_details.deleted}')
    if result.commit_details.modified: commit_details.append(f'~{result.commit_details.modified}')
    commit_details = ', '.join(commit_details)
    if commit_details: details.append(f'({commit_details})')

    push_details = []
    if result.push_details.to_push: push_details.append(f'↑{result.push_details.to_push}')
    if result.push_details.to_pull: push_details.append(f'↓{result.push_details.to_pull}')
    if result.push_details.error: push_details.append(f'!{result.push_details.error}')
    push_details = ', '.join(push_details)
    if push_details: details.append(f'({push_details})')

    details = ' '.join(details)
    details = (' ' + details).rstrip()
    print(f'[{committed}][{pushed}] {directory}{details}')

def gitcheckup_all(do_fetch=False):
    try:
        directories = read_directories_file()
    except FileNotFoundError as exc:
        print(f'Please put your git repo locations in {exc.filename}.')
        return 1

    for directory in directories:
        gitcheckup_one(directory, do_fetch=do_fetch)

def gitcheckup_argparse(args):
    return gitcheckup_all(do_fetch=args.do_fetch)

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('--fetch', dest='do_fetch', action='store_true')
    parser.set_defaults(func=gitcheckup_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
