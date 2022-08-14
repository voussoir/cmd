import argparse
import io
import json
import requests
import sys
import tenacity
import traceback
import zipfile

from voussoirkit import betterhelp
from voussoirkit import downloady
from voussoirkit import httperrors
from voussoirkit import operatornotify
from voussoirkit import pathclass
from voussoirkit import pipeable
from voussoirkit import progressbars
from voussoirkit import vlogging

log = vlogging.getLogger(__name__, 'fdroidapk')
vlogging.getLogger('urllib3').setLevel(vlogging.SILENT)
vlogging.getLogger('voussoirkit.downloady').setLevel(vlogging.WARNING)

session = requests.Session()
my_tenacity = tenacity.retry(
    retry=tenacity.retry_if_exception_type(requests.exceptions.ConnectionError),
    stop=tenacity.stop_after_attempt(5),
    wait=tenacity.wait_exponential(multiplier=2, min=3, max=60),
    reraise=True,
)

@my_tenacity
def download_file(url, path):
    return downloady.download_file(
        url,
        path,
        progressbar=progressbars.bar1_bytestring,
        timeout=30,
    )

def get_fdroid_index():
    '''
    Download the index-v1.json and return it as a dict.
    '''
    log.info('Downloading F-Droid package index.')
    url = 'https://f-droid.org/repo/index-v1.jar'
    response = requests.get(url)
    httperrors.raise_for_status(response)
    zf = zipfile.ZipFile(io.BytesIO(response.content))
    index = json.load(zf.open('index-v1.json', 'r'))
    return index

def ls_packages(path):
    packages = set()
    items = path.listdir()
    for item in items:
        if item.is_dir and '.' in item.basename:
            packages.add(item.basename)
        elif item.is_file and item.extension == 'apk':
            package = item.basename.split('-')[0]
            packages.add(package)
    return sorted(packages)

def normalize_package_name(package_name):
    package_name = package_name.strip()
    # If it happens to be a URL.
    package_name = package_name.strip('/')
    package_name = package_name.rsplit('/', 1)[-1]
    return package_name

@pipeable.ctrlc_return1
def fpk_argparse(args):
    args.destination.assert_is_directory()

    return_status = 0

    packages = args.packages
    if packages == ['*']:
        packages = ls_packages(pathclass.cwd())

    download_count = 0

    index = get_fdroid_index()

    for package in packages:
        package = normalize_package_name(package)

        try:
            this_packages = index['packages'][package]
        except KeyError:
            log.error('%s is not in the package index.', package)
            return_status = 1
            continue

        most_recent = sorted(this_packages, key=lambda p: p['versionCode'])[-1]
        apk_basename = most_recent['apkName']
        log.debug('Most recent is %s', apk_basename)
        apk_url = f'https://f-droid.org/repo/{apk_basename}'

        if args.folders:
            this_dest = args.destination.with_child(package)
            this_dest.makedirs(exist_ok=True)
        else:
            this_dest = args.destination
        this_dest = this_dest.with_child(apk_basename)

        if this_dest.exists:
            log.debug('%s exists.', this_dest.absolute_path)
            continue

        log.info('Downloading %s.', this_dest.absolute_path)

        try:
            download_file(apk_url, this_dest)
            download_count += 1
        except Exception as exc:
            exc = traceback.format_exc()
            log.error('%s was unable to download apk:\n%s', package, exc)
            return_status = 1
            continue

    log.info('Downloaded %d apks.', download_count)

    return return_status

@operatornotify.main_decorator(subject='fdroidapk.py')
@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser(description='F-Droid APK downloader.')

    parser.add_argument(
        'packages',
        nargs='+',
        type=str,
        help='''
        One or more package names to download, separated by spaces. You can find
        the package name in the URL on f-droid.org.
        For example, com.nutomic.syncthingandroid from the URL
        https://f-droid.org/en/packages/com.nutomic.syncthingandroid/
        ''',
    )
    parser.add_argument(
        '--folders',
        action='store_true',
        help='''
        If provided, each apk will be downloaded into a separate folder named after
        the package.
        If omitted, the apks are downloaded into the destination folder directly.
        ''',
    )
    parser.add_argument(
        '--destination',
        default=pathclass.cwd(),
        type=pathclass.Path,
        help='''
        Alternative path to download the apk files to. Default is cwd.
        ''',
    )
    parser.set_defaults(func=fpk_argparse)

    return betterhelp.go(parser, argv)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
