'''
gitcheckup
==========

This program helps you check the commit and push status of your favorite git
repositories. The output looks like this:

[ ][P] D:\\Git\\cmd (~1)
[C][P] D:\\Git\\Etiquette
[ ][P] D:\\Git\\voussoirkit (+1)
[C][ ] D:\\Git\\YCDL (↑3)

To specify the list of git directories, you may either:
- Create a gitcheckup.txt file in the same directory as this file, where every
  line contains an absolute path to the directory, or
- Pass directories as a series of positional arguments to this program.

> gitcheckup.py <flags>
> gitcheckup.py dir1 dir2 <flags>

flags:
--fetch:
    Run `git fetch --all` in each directory.

--pull:
    Run `git pull --all` in each directory.

--push:
    Run `git push` in each directory.

--add path:
    Add path to the gitcheckup.txt file.

--remove path:
    Remove path from the gitcheckup.txt file.

Examples:
> gitcheckup
> gitcheckup --fetch
> gitcheckup D:\\Git\\cmd D:\\Git\\YCDL --pull
'''
import argparse
import os
import subprocess
import sys

from voussoirkit import betterhelp
from voussoirkit import dotdict
from voussoirkit import pathclass
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
    output = output.decode().strip()
    return output

def add_directory(directory):
    '''
    Add a directory to the gitcheckup.txt file, creating that file if it does
    not exist.
    '''
    directory = pathclass.Path(directory)

    try:
        directories = set(read_directories_file())
    except NoConfigFile:
        directories = set()

    directories.add(directory)
    write_directories_file(directories)

def remove_directory(directory):
    '''
    Remove a directory from the gitcheckup.txt file.
    Raise NoConfigFile if it does not exist.
    '''
    directory = pathclass.Path(directory)
    directories = set(read_directories_file())
    try:
        directories.remove(directory)
    except KeyError:
        return
    write_directories_file(directories)

def read_directories_file():
    '''
    Return a list of pathclass.Path from the lines of gitcheckup.txt.
    Raise NoConfigFile if it does not exist.
    '''
    directories_file = pathclass.Path(__file__).parent.with_child('gitcheckup.txt')

    try:
        handle = directories_file.open('r', encoding='utf-8')
    except FileNotFoundError as exc:
        raise NoConfigFile(exc.filename) from exc

    with handle:
        directories = handle.readlines()

    directories = [line.strip() for line in directories]
    directories = [line for line in directories if line]
    directories = [pathclass.Path(line) for line in directories]

    return directories

def write_directories_file(directories):
    '''
    Write a list of directories to the gitcheckup.txt file.
    '''
    directories = [pathclass.Path(d) for d in directories]
    directories = sorted(directories)
    directories = [d.correct_case() for d in directories]
    directories = [d.absolute_path for d in directories]

    directories_file = pathclass.Path(__file__).parent.with_child('gitcheckup.txt')

    handle = directories_file.open('w', encoding='utf-8')

    with handle:
        handle.write('\n'.join(directories))

# GIT FUNCTIONS
################################################################################
def git_commits_between(a, b):
    command = [GIT, 'log', '--oneline', f'{a}..{b}']
    output = check_output(command)
    lines = output.splitlines()
    return lines

def git_current_branch():
    command = [GIT, 'rev-parse', '--abbrev-ref', 'HEAD']
    return check_output(command)

def git_fetch():
    command = [GIT, 'fetch', '--all']
    return check_output(command)

def git_merge_base():
    command = [GIT, 'merge-base', '@', '@{u}']
    return check_output(command)

def git_pull():
    command = [GIT, 'pull', '--all']
    return check_output(command)

def git_push():
    command = [GIT, 'push']
    return check_output(command)

def git_rev_parse(rev):
    command = [GIT, 'rev-parse', rev]
    return check_output(command)

def git_status():
    command = [GIT, 'status', '--short', '--untracked-files=all']
    return check_output(command)

# CHECKUP
################################################################################
def checkup_committed():
    details = dotdict.DotDict(default=None)

    details.added = 0
    details.modified = 0
    details.deleted = 0

    for line in git_status().splitlines():
        status = line.split()[0].strip()

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

    my_head = git_rev_parse('@')

    try:
        remote_head = git_rev_parse('@{u}')
    except subprocess.CalledProcessError as exc:
        current_branch = git_current_branch()
        details.error = NoUpstreamBranch(current_branch)
        return details

    if my_head == remote_head:
        details.to_push = 0
        details.to_pull = 0
    else:
        try:
            merge_base = git_merge_base()
        except subprocess.CalledProcessError as exc:
            # This happens when the repository has been completely rewritten
            # with a new root.
            details.error = 'Root commit has changed'
            return details

        if my_head == merge_base:
            details.to_push = 0
            details.to_pull = len(git_commits_between(merge_base, remote_head))
        elif remote_head == merge_base:
            details.to_push = len(git_commits_between(merge_base, my_head))
            details.to_pull = 0
        else:
            details.to_push = len(git_commits_between(merge_base, my_head))
            details.to_pull = len(git_commits_between(merge_base, remote_head))

    all_pushed = (details.to_push, details.to_pull) == (0, 0)
    details.pushed = all_pushed
    return details

def gitcheckup(directory, do_fetch=False, do_pull=False, do_push=False):
    os.chdir(directory.absolute_path)

    if do_fetch:
        git_fetch()

    if do_pull:
        git_pull()

    if do_push:
        git_push()

    commit_details = checkup_committed()
    push_details = checkup_pushed()

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
    print(f'[{committed}][{pushed}] {directory.absolute_path}{details}')

# COMMAND LINE
################################################################################
def gitcheckup_argparse(args):
    if args.add_directory is not None:
        add_directory(args.add_directory)

    if args.remove_directory is not None:
        remove_directory(args.remove_directory)

    if args.directories:
        directories = [pathclass.Path(d) for d in args.directories]
    else:
        directories = read_directories_file()

    try:
        for directory in directories:
            gitcheckup(directory, do_fetch=args.do_fetch, do_pull=args.do_pull, do_push=args.do_push)
    except subprocess.CalledProcessError as exc:
        sys.stdout.write(f'{exc.cmd} exited with status {exc.returncode}\n')
        sys.stdout.write(exc.output.decode())
        return 1

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('directories', nargs='*')
    parser.add_argument('--fetch', dest='do_fetch', action='store_true')
    parser.add_argument('--pull', dest='do_pull', action='store_true')
    parser.add_argument('--push', dest='do_push', action='store_true')
    parser.add_argument('--add', dest='add_directory')
    parser.add_argument('--remove', dest='remove_directory')
    parser.set_defaults(func=gitcheckup_argparse)

    try:
        return betterhelp.single_main(argv, parser, docstring=__doc__)
    except GitCheckupException as exc:
        print(exc)
        return 1

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
