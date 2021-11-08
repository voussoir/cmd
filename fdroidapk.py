'''
fdroidapk - F-Droid APK downloader
==================================

> fdroidapk package_names <flags>

package_names:
    One or more package names to download, separated by spaces. You can find
    the package name in the URL on f-droid.org.
    For example, com.nutomic.syncthingandroid from the URL
    https://f-droid.org/en/packages/com.nutomic.syncthingandroid/

--destination path:
    Alternative path to download the apk files to. Default is cwd.

--folders:
    If provided, each apk will be downloaded into a separate folder named after
    the package.
'''
import argparse
import bs4
import requests
import sys
import tenacity

from voussoirkit import betterhelp
from voussoirkit import downloady
from voussoirkit import operatornotify
from voussoirkit import pathclass
from voussoirkit import pipeable
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
        callback_progress=downloady.Progress2,
        timeout=30,
    )

@my_tenacity
def get_apk_url(package_name):
    url = f'https://f-droid.org/en/packages/{package_name}'
    log.debug('Downloading page %s.', url)
    response = session.get(url, timeout=30)
    response.raise_for_status()
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    li = soup.find('li', {'class': 'package-version'})
    aa = li.find_all('a')
    aa = [a for a in aa if a.get('href', '').endswith('.apk')]
    apk_url = aa[0]['href']
    return apk_url

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
    destination = pathclass.Path(args.destination)
    destination.assert_is_directory()

    return_status = 0

    packages = args.packages
    if packages == ['*']:
        packages = ls_packages(pathclass.cwd())

    for package in packages:
        package = normalize_package_name(package)
        log.info('Checking %s.', package)

        try:
            apk_url = get_apk_url(package)
        except Exception as exc:
            log.error('%s was unable to get apk url (%s).', package, exc)
            return_status = 1
            continue

        apk_basename = downloady.basename_from_url(apk_url)
        if args.folders:
            this_dest = destination.with_child(package)
            this_dest.makedirs(exist_ok=True)
        else:
            this_dest = destination
        this_dest = this_dest.with_child(apk_basename)

        if this_dest.exists:
            log.debug('%s exists.', this_dest.absolute_path)
            continue

        log.info('Downloading %s.', this_dest.absolute_path)

        try:
            download_file(apk_url, this_dest)
        except Exception as exc:
            log.error('%s was unable to download apk (%s).', package, exc)
            return_status = 1
            continue

    return return_status

@operatornotify.main_decorator(subject='fdroidapk.py')
@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('packages', nargs='+')
    parser.add_argument('--folders', action='store_true')
    parser.add_argument('--destination', default='.')
    parser.set_defaults(func=fpk_argparse)

    return betterhelp.single_main(argv, parser, __doc__)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
