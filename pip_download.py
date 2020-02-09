'''
Wraps `pip download` so that the resulting files, including dependencies,
are automatically organized into a folder called .\package\package-version.
'''
import argparse
import os
import subprocess
import sys
import tempfile

def clean_version(version):
    for (index, character) in enumerate(version):
        if character not in '.0123456789':
            break
    else:
        return version
    return version[:index]

def pip_download(package):
    tmpdir = tempfile.TemporaryDirectory(prefix=f'pip_download-{package}')
    subprocess.call([sys.executable, '-m', 'pip', 'download', package, '-d', tmpdir.name, '--no-cache-dir'])
    downloaded_files = os.listdir(tmpdir.name)
    for filename in downloaded_files:
        filename = filename.lower()
        prefix = package.lower() + '-'
        if filename.startswith(prefix):
            parts = filename.replace(prefix, '')
            parts = parts.split('-')
            version = parts[0]
            break
    else:
        raise Exception(f'None of the downloads match the package name {package}? {downloaded_files}')
    version = clean_version(version)
    new_directory = f'{package}\\{package}-{version}'
    if not os.path.exists(new_directory):
        os.makedirs(new_directory)
        for filename in downloaded_files:
            os.rename(os.path.join(tmpdir.name, filename), os.path.join(new_directory, filename))
    tmpdir.cleanup()


def pip_download_argparse(args):
    for package in args.packages:
        pip_download(package)

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('packages', nargs='+')
    parser.set_defaults(func=pip_download_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
