'''
Copy your file every few minutes while you work on it, so that you can have snapshots of its history.
Not a replacement for real version control but could be applicable in very simple situations or in
cases where e.g. git is not.
'''
import argparse
import hashlib
import os
import shutil
import sys
import time

from voussoirkit import bytestring
from voussoirkit import pathclass
from voussoirkit import winglob

def hash_file(filepath, hasher):
    bytestream = read_filebytes(filepath)
    for chunk in bytestream:
        hasher.update(chunk)
    return hasher.hexdigest()

def hash_file_md5(filepath):
    return hash_file(filepath, hasher=hashlib.md5())

def read_filebytes(filepath, chunk_size=bytestring.MIBIBYTE):
    '''
    Yield chunks of bytes from the file between the endpoints.
    '''
    filepath = pathclass.Path(filepath)
    if not filepath.is_file:
        raise FileNotFoundError(filepath)

    f = open(filepath.absolute_path, 'rb')
    with f:
        while True:
            chunk = f.read(chunk_size)
            if len(chunk) == 0:
                break

            yield chunk

def filetimelapse(filepath, rate):
    (noext, extension) = os.path.splitext(filepath)

    last_hash = None
    existing_timelapses = winglob.glob(f'{noext}-*.filetimelapse{extension}')
    if existing_timelapses:
        last_hash = hash_file_md5(existing_timelapses[-1])
        print(f'Starting with previous {existing_timelapses[-1]} {last_hash}')

    while True:
        new_hash = hash_file_md5(filepath)
        if new_hash != last_hash:
            timestamp = time.strftime('%Y%m%d%H%M%S')
            copy_name = f'{noext}-{timestamp}.filetimelapse{extension}'
            shutil.copy(filepath, copy_name)
            last_hash = new_hash
            print(copy_name, new_hash)
        time.sleep(rate)

def filetimelapse_argparse(args):
    return filetimelapse(args.filepath, args.rate)

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('filepath')
    parser.add_argument('--rate', dest='rate', default=None, required=True, type=int)
    parser.set_defaults(func=filetimelapse_argparse)

    args = parser.parse_args(argv)
    args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
