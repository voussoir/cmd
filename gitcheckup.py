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

# Here is an example of typical `git log --oneline --branches --not --remotes` output:
# Only the commits that haven't been pushed to a remote are shown!
# Thank you cxreg https://stackoverflow.com/a/3338774
#
# a755f32 Ready to publish
# 5602e1e Another commit message
# a32a372 My commit message

def checkup_committed(directory):
    os.chdir(directory)
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
        details = f'(+{added}, -{deleted}, ~{modified})'

    return (committed, details)

def checkup_pushed(directory):
    os.chdir(directory)
    command = [GIT, 'log', '--oneline', '--branches', '--not', '--remotes']
    output = subprocess.check_output(command, stderr=subprocess.STDOUT)

    commits = sum(1 for line in output.splitlines() if line.strip())

    if commits == 0:
        pushed = True
        details = ''
    else:
        pushed = False
        details = f'(↑{commits})'

    return (pushed, details)

def checkup(directory):
    (committed, commit_details) = checkup_committed(directory)
    (pushed, push_details) = checkup_pushed(directory)
    return {
        'committed': committed,
        'commit_details': commit_details,
        'pushed': pushed,
        'push_details': push_details,
    }

def main(argv):
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
        result = checkup(directory)
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

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
