import argparse
import os
import re
import subprocess
import sys

from voussoirkit import betterhelp
from voussoirkit import dotdict
from voussoirkit import pathclass
from voussoirkit import subproctools
from voussoirkit import vlogging
from voussoirkit import winwhich

log = vlogging.getLogger(__name__, 'gitcheckup')

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
    log.debug(subproctools.format_command(command))
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
        directories = directories_file.readlines('r', encoding='utf-8')
    except FileNotFoundError as exc:
        raise NoConfigFile(exc.filename) from exc

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

    directories_file.write('w', '\n'.join(directories), encoding='utf-8')

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

def git_push_all():
    remotes = git_remotes()
    branch = git_current_branch()
    for remote in remotes:
        git_push(remote, branch)

def git_push(remote=None, branch=None):
    command = [GIT, 'push']
    if remote:
        command.append(remote)
    if branch:
        command.append(branch)
    return check_output(command)

def git_remotes():
    command = [GIT, 'remote']
    remotes = check_output(command).splitlines()
    return remotes

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

    try:
        my_head = git_rev_parse('@')
    except subprocess.CalledProcessError as exc:
        details.error = 'No HEAD'
        return details

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

def gitcheckup(
        directory,
        do_fetch=False,
        do_pull=False,
        do_push=False,
        run_command=None,
    ):
    log.debug('gitcheckup in %s', directory.absolute_path)
    os.chdir(directory.absolute_path)

    if run_command:
        command = [GIT, *run_command]
        check_output(command)
    else:
        if do_fetch:
            git_fetch()

        if do_pull:
            git_pull()

        if do_push:
            git_push_all()

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

    if args.run_command:
        args.run_command = [re.sub(r'^\\-', '-', arg) for arg in args.run_command]

    try:
        for directory in directories:
            gitcheckup(
                directory,
                do_fetch=args.do_fetch,
                do_pull=args.do_pull,
                do_push=args.do_push,
                run_command=args.run_command,
            )
    except subprocess.CalledProcessError as exc:
        sys.stdout.write(f'{exc.cmd} exited with status {exc.returncode}\n')
        sys.stdout.write(exc.output.decode())
        return 1

@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser(
        description='''
        This program helps you check the commit and push status of your favorite git
        repositories. The output looks like this:

        [ ][P] D:\\Git\\cmd (~1)
        [C][P] D:\\Git\\Etiquette
        [ ][P] D:\\Git\\voussoirkit (+1)
        [C][ ] D:\\Git\\YCDL (↑3)
        ''',
    )
    parser.examples = [
        '',
        '--fetch',
        'D:\\Git\\cmd D:\\Git\\YCDL --pull',
        '--run add README.md',
    ]

    parser.add_argument(
        'directories',
        nargs='*',
        help='''
        One or more directories to check up.
        If omitted, you should have a file called gitcheckup.txt in the same
        directory as this file, where every line contains an absolute path to
        a directory.
        ''',
    )
    parser.add_argument(
        '--fetch',
        dest='do_fetch',
        action='store_true',
        help='''
        Run `git fetch --all` in each directory.
        ''',
    )
    parser.add_argument(
        '--pull',
        dest='do_pull',
        action='store_true',
        help='''
        Run `git pull --all` in each directory.
        ''',
    )
    parser.add_argument(
        '--push',
        dest='do_push',
        action='store_true',
        help='''
        Run `git push` in each directory.
        ''',
    )
    parser.add_argument(
        '--run',
        dest='run_command',
        nargs='+',
        type=str,
        help='''
        Run `git <command>` in each directory. You can use \- to escape - in your
        git arguments, since they would confuse this program's argparse.
        If this is used, any --fetch, --pull, --push is ignored.
        ''',
    )
    parser.add_argument(
        '--add',
        dest='add_directory',
        metavar='path',
        type=str,
        help='''
        Add path to the gitcheckup.txt file.
        ''',
    )
    parser.add_argument(
        '--remove',
        dest='remove_directory',
        metavar='path',
        type=str,
        help='''
        Remove path from the gitcheckup.txt file.
        ''',
    )
    parser.set_defaults(func=gitcheckup_argparse)

    try:
        return betterhelp.go(parser, argv)
    except GitCheckupException as exc:
        print(exc)
        return 1

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
