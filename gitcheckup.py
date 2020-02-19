import argparse
import os
import subprocess
import sys
import types

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
    pass

def check_output(command):
    output = subprocess.check_output(command, stderr=subprocess.STDOUT)
    return output

def checkup_committed():
    command = [GIT, 'status', '--short', '--untracked-files=all']
    output = check_output(command)

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

    committed = (added, modified, deleted) == (0, 0, 0)
    details = types.SimpleNamespace(added=added, deleted=deleted, modified=modified)

    return (committed, details)

def checkup_pushed():
    command = [GIT, 'rev-parse', '@']
    my_head = check_output(command).strip().decode()

    command = [GIT, 'rev-parse', '@{u}']
    try:
        remote_head = check_output(command).strip().decode()
    except subprocess.CalledProcessError as exc:
        command = [GIT, 'rev-parse', '--abbrev-ref', 'HEAD']
        current_branch = check_output(command).strip().decode()
        raise NoUpstreamBranch(current_branch)

    if my_head == remote_head:
        to_push = 0
        to_pull = 0
    else:
        command = [GIT, 'merge-base', '@', '@{u}']
        merge_base = check_output(command)
        merge_base = merge_base.strip().decode()

        if my_head == merge_base:
            to_push = 0
            to_pull = len(git_commits_between(merge_base, remote_head))
        elif remote_head == merge_base:
            to_push = len(git_commits_between(merge_base, my_head))
            to_pull = 0
        else:
            to_push = len(git_commits_between(merge_base, my_head))
            to_pull = len(git_commits_between(merge_base, remote_head))

    pushed = (to_push, to_pull) == (0, 0)
    details = types.SimpleNamespace(
        to_push=to_push,
        to_pull=to_pull,
    )

    return (pushed, details)

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
    (committed, commit_details) = checkup_committed()
    (pushed, push_details) = checkup_pushed()
    return types.SimpleNamespace(
        committed=committed,
        commit_details=commit_details,
        pushed=pushed,
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

def gitcheckup(do_fetch=False):
    try:
        directories = read_directories_file()
    except FileNotFoundError as exc:
        print(f'Please put your git repo locations in {exc.filename}.')
        return 1

    for directory in directories:
        try:
            result = checkup(directory, do_fetch=do_fetch)
        except subprocess.CalledProcessError as exc:
            raise Exception(exc.output)

        committed = 'C' if result.committed else ' '
        pushed = 'P' if result.pushed else ' '

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
        push_details = ', '.join(push_details)
        if push_details: details.append(f'({push_details})')

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
