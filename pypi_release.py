'''
pypi_release
============

This script helps me release voussoirkit on pypi.

--major,
--minor,
--patch:
    Pass only one of these. The version number of your package will increase by
    1 in either the major, minor, or patch.

--do-tag:
    If this argument is passed, a git tag will be added to the release commit.
'''
import argparse
import re
import shutil
import subprocess
import sys
import textwrap
import time

from voussoirkit import interactive
from voussoirkit import niceprints
from voussoirkit import passwordy
from voussoirkit import vlogging
from voussoirkit import winwhich

log = vlogging.getLogger(__name__, 'pypi_release')

GIT = winwhich.which('git')
PY = winwhich.which('py')
TWINE = winwhich.which('twine')

BUMP_PATTERN = r'Bump to version (\d+\.\d+\.\d+)\.'

class PypiReleaseError(Exception):
    pass

class BadSetup(PypiReleaseError):
    pass

class DirtyState(PypiReleaseError):
    pass

class NotSemver(PypiReleaseError):
    pass

class VersionOutOfOrder(PypiReleaseError):
    pass

# HELPER FUNCTIONS
################################################################################
def bump_version(version, versionbump):
    (major, minor, patch) = [int(x) for x in version.split('.')]
    if versionbump == 'major':
        major += 1
        minor = 0
        patch = 0
    elif versionbump == 'minor':
        minor += 1
        patch = 0
    elif versionbump == 'patch':
        patch += 1
    else:
        raise ValueError(f'versionbump should be major, minor, or patch, not {versionbump}.')
    version = f'{major}.{minor}.{patch}'
    return version

def check_call(command):
    log.debug(format_command(command))
    return subprocess.check_call(command)

def check_output(command):
    log.debug(format_command(command))
    return subprocess.check_output(command, stderr=subprocess.STDOUT)

def pick_versionbump(major, minor, patch):
    mmp = (major, minor, patch)
    if not all(b in [True, False, None] for b in mmp):
        raise TypeError('major, minor, patch should all be True, False, or None.')

    if mmp in [(False, False, False), (None, None, None)]:
        versionbump = 'patch'

    elif mmp.count(True) > 1:
        raise TypeError('Must only pick one of major, minor, patch.')

    elif major:
        versionbump = 'major'

    elif minor:
        versionbump = 'minor'

    elif patch:
        versionbump = 'patch'

    else:
        raise TypeError()

    return versionbump

def format_command(command):
    cmd = [('"%s"' % x) if (' ' in x or x == '') else x for x in command]
    cmd = ' '.join(cmd)
    cmd = cmd.strip()
    cmd = cmd.replace(GIT, 'git')
    cmd = cmd.replace(PY, 'py')
    cmd = cmd.replace(TWINE, 'twine')
    print(f'> {cmd}')

def semver_split(semver):
    original = semver
    try:
        semver = semver.strip('v')
        mmp = semver.split('.')
        mmp = tuple(int(x) for x in mmp)
        (major, minor, patch) = mmp
        return mmp
    except Exception:
        raise NotSemver(original)

def slowprint(s=None):
    slow = 0.05
    if s is None:
        print()
        time.sleep(slow)
        return
    for line in s.split('\n'):
        print(line)
        time.sleep(slow)

# SETUP.PY
################################################################################
def extract_info_from_setup():
    handle = open('setup.py', 'r', encoding='utf-8')
    with handle:
        setup_py = handle.read()

    name = re.findall(r'''\bname=["']([A-Za-z0-9_-]+)["']''', setup_py)
    if len(name) != 1:
        raise BadSetup(f'Expected to find 1 name but found {len(name)}.')
    name = name[0]

    version = re.findall(r'''\bversion=["'](\d+\.\d+\.\d+)["']''', setup_py)
    if len(version) != 1:
        raise BadSetup(f'Expected to find 1 version but found {len(version)}.')
    version = version[0]

    return (setup_py, name, version)

def update_info_in_setup(setup_py, name, version):
    re_from = fr'''\bname=(["'])({name})(["'])'''
    re_to = fr'''name=\1\2\3'''
    setup_py = re.sub(re_from, re_to, setup_py)

    re_from = fr'''\bversion=(["'])(\d+\.\d+\.\d+)(["'])'''
    re_to = fr'''version=\g<1>{version}\g<3>'''
    setup_py = re.sub(re_from, re_to, setup_py)
    return setup_py

def write_setup(setup_py):
    handle = open('setup.py', 'w', encoding='utf-8')
    with handle:
        handle.write(setup_py)

# GIT
################################################################################
def git_assert_current_greater_than_latest(latest_release_version, new_version):
    if latest_release_version >= semver_split(new_version):
        msg = f'New version should be {new_version} but {latest_release_version} already exists.'
        raise VersionOutOfOrder(msg)

def git_assert_no_stashes():
    command = [GIT, 'stash', 'list']
    output = check_output(command)
    lines = output.strip().splitlines()
    if len(lines) != 0:
        raise DirtyState('Please ensure there are no stashes.')

def git_assert_pushable():
    command = [GIT, 'fetch', '--all']
    check_call(command)

    command = [GIT, 'merge-base', '@', '@{u}']
    merge_base = check_output(command).strip()

    command = [GIT, 'rev-parse', '@']
    my_head = check_output(command).strip()

    command = [GIT, 'rev-parse', '@{u}']
    remote_head = check_output(command).strip()

    if my_head == remote_head:
        pass
    elif my_head == merge_base:
        git_commits_since(merge_base.decode(), show=True, inclusive=True)
        raise DirtyState('Cant push, need to pull first.')
    elif remote_head == merge_base:
        pass
    else:
        git_commits_since(merge_base.decode(), show=True, inclusive=True)
        raise DirtyState('Cant push, diverged from remote.')

def git_commit_bump(version):
    command = [GIT, 'add', 'setup.py']
    check_call(command)

    command = [GIT, 'commit', '-m', f'Bump to version {version}.']
    check_call(command)

def git_commits_since(commit, show, inclusive=False):
    if commit:
        if inclusive:
            commit += '~1'
        command = [GIT, '--no-pager', 'log', '--oneline', '--graph', '--branches', '--remotes', f'{commit}..']
    else:
        command = [GIT, '--no-pager', 'log', '--oneline', '--graph']

    if show:
        check_call(command)
    else:
        output = check_output(command)
        lines = output.strip().splitlines()
        return lines

def git_current_remote_branch():
    command = [GIT, 'rev-parse', '--abbrev-ref', '--symbolic-full-name', '@{u}']
    output = check_output(command)
    output = output.strip().decode()
    (remote, branch) = output.split('/')
    return (remote, branch)

def git_determine_latest_release():
    (latest_tagged_commit, latest_tag_version) = git_latest_tagged_commit()
    (latest_bump_commit, latest_bump_version) = git_latest_bump_commit()

    if latest_tagged_commit is None:
        latest_release_commit = latest_bump_commit
        latest_release_version = latest_bump_version

    elif latest_bump_commit is None:
        latest_release_commit = latest_tagged_commit
        latest_release_version = latest_tag_version

    elif latest_tag_version > latest_bump_version:
        latest_release_commit = latest_tagged_commit
        latest_release_version = latest_tag_version

    else:
        latest_release_commit = latest_bump_commit
        latest_release_version = latest_bump_version

    return (latest_release_commit, latest_release_version)

def git_latest_bump_commit():
    command = [GIT, 'log', '--oneline', '--no-abbrev-commit', '--grep', 'Bump to version *.', '-1']
    output = check_output(command)
    output = output.strip()
    if not output:
        return (None, None)
    commit = output.splitlines()[0].decode()
    version = re.search(BUMP_PATTERN, commit).group(1)
    version = semver_split(version)
    commit = commit.split()[0]
    return (commit, version)

def git_latest_tagged_commit():
    command = [GIT, 'log', '--oneline', '--no-abbrev-commit', '--tags=v*.*.*', '-1']
    output = check_output(command)
    output = output.strip()
    if not output:
        return (None, None)

    commit = output.splitlines()[0].decode().split()[0]

    for tag in git_tags_on_commit(commit):
        try:
            version = semver_split(tag)
            break
        except NotSemver:
            pass
    else:
        return (None, None)

    return (commit, version)

def git_push(remote, branch):
    command = [GIT, 'push', remote, branch]
    check_call(command)

def git_push_tag(remote, tag):
    command = [GIT, 'push', remote, tag]
    check_call(command)

def git_show_commit(commit):
    command = [GIT, 'show', '--oneline', '-s', commit]
    check_call(command)

def git_stash_push():
    token = passwordy.urandom_hex(32)
    command = [GIT, 'stash', 'push', '--include-untracked', '--message', token]
    output = check_output(command)

    command = [GIT, 'stash', 'list', '--grep', token]
    output = check_output(command).strip()

    did_stash = bool(output)
    return did_stash

def git_stash_restore():
    command = [GIT, 'stash', 'pop']
    check_call(command)

def git_tag_version(tag):
    command = [GIT, 'tag', '-a', tag, '-m', '']
    check_call(command)

def git_tags_on_commit(commit):
    command = [GIT, 'tag', '--points-at', commit]
    output = check_output(command)
    output = output.strip()
    if not output:
        return []
    output = output.decode().splitlines()
    return output

# PYPI
################################################################################
def pypi_upload(name):
    egg_dir = f'{name}.egg-info'

    command = [PY, 'setup.py', 'sdist']
    check_call(command)

    command = [TWINE, 'upload', '-r', 'pypi', 'dist\\*']
    check_call(command)

    shutil.rmtree('dist')
    shutil.rmtree(egg_dir)

def pypi_release(do_tag=False, versionbump='patch'):
    git_assert_no_stashes()
    git_assert_pushable()

    (setup_py, name, old_version) = extract_info_from_setup()
    new_version = bump_version(old_version, versionbump)
    new_tag = f'v{new_version}'

    (latest_release_commit, latest_release_version) = git_determine_latest_release()

    git_assert_current_greater_than_latest(latest_release_version, new_version)

    commits_since_last_release = git_commits_since(latest_release_commit, show=False)
    if len(commits_since_last_release) == 0:
        print('No new commits to release')
        return

    (remote, branch) = git_current_remote_branch()

    print(niceprints.solid_hash_header(f'{name} {new_version}'))

    slowprint(f'Upgrading {name} from {old_version} --> {new_version}.')
    slowprint()

    if latest_release_commit:
        slowprint('Latest release:')
        git_show_commit(latest_release_commit)
        slowprint()

    slowprint('This release:')
    git_commits_since(latest_release_commit, show=True)
    slowprint()

    setup_py = update_info_in_setup(setup_py, name, new_version)
    slowprint('Rewrite setup.py:')
    slowprint(textwrap.indent(setup_py, '>>> '))
    slowprint()

    slowprint(f'Release will be pushed to {remote} {branch}.')

    print(niceprints.solid_hash_header(f'{name} {new_version}'))

    if not interactive.getpermission(f'READY TO RELEASE {name} {new_version}.'):
        return

    write_setup(setup_py)

    git_commit_bump(new_version)
    if do_tag:
        git_tag_version(new_tag)

    git_push(remote, branch)
    if do_tag:
        git_push_tag(remote, new_tag)

    did_stash = git_stash_push()
    pypi_upload(name)
    if did_stash:
        git_stash_restore()

    git_commits_since(latest_release_commit, show=True)

def pypi_release_argparse(args):
    versionbump = pick_versionbump(args.major, args.minor, args.patch)
    try:
        return pypi_release(do_tag=args.do_tag, versionbump=versionbump)
    except subprocess.CalledProcessError as exc:
        print(exc.output)
        return 1

@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('--major', action='store_true')
    parser.add_argument('--minor', action='store_true')
    parser.add_argument('--patch', action='store_true')
    parser.add_argument('--do_tag', '--do-tag', action='store_true')
    parser.set_defaults(func=pypi_release_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
