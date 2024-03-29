import argparse
import collections
import os
import shutil
import sys

from voussoirkit import passwordy
from voussoirkit import pathclass
from voussoirkit import vlogging

log = vlogging.getLogger(__name__, 'sole_subdir_lift')

def sole_lift_argparse(args):
    starting = pathclass.Path(args.starting)
    queue = collections.deque()
    queue.extend(starting.walk_directories())
    while len(queue) > 0:
        directory = queue.popleft()

        if not directory.exists:
            log.debug('%s no longer exists.', directory)
            continue

        if directory not in starting:
            log.debug('%s is outside of starting.', directory)
            continue

        children = directory.listdir()
        child_count = len(children)
        if child_count != 1:
            log.debug('%s has %d children.', directory, child_count)
            continue

        child = children[0]

        if not child.is_dir:
            log.debug('%s contains a file, not a dir.', directory)
            continue

        log.info('Lifting contents of %s.', child.absolute_path)
        # child is renamed to random hex so that the grandchildren we are about
        # to lift don't have name conflicts with the child dir itself.
        # Consider .\abc\abc where the grandchild can't be moved.
        temp_dir = directory.with_child(passwordy.random_hex(32))
        os.rename(child, temp_dir)
        for grandchild in temp_dir.listdir():
            shutil.move(grandchild, directory)

        if temp_dir.listdir():
            raise Exception('The temp dir is supposed to be empty by this point.')

        os.rmdir(temp_dir)
        queue.append(directory.parent)

    return 0

@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('starting', nargs='?', default='.')
    parser.set_defaults(func=sole_lift_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
