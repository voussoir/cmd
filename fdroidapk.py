import argparse
import bs4
import requests
import sys
import time

from voussoirkit import backoff
from voussoirkit import betterhelp
from voussoirkit import downloady
from voussoirkit import pathclass
from voussoirkit import vlogging

log = vlogging.getLogger(__name__, 'fpk')

session = requests.Session()

def get_apk_url(package_name):
    url = f'https://f-droid.org/en/packages/{package_name}'
    log.debug('Downloading page %s', url)
    response = session.get(url, timeout=30)
    response.raise_for_status()
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    li = soup.find('li', {'class': 'package-version'})
    aa = li.find_all('a')
    aa = [a for a in aa if a.get('href', '').endswith('.apk')]
    apk_url = aa[0]['href']
    return apk_url

def normalize_package_name(package_name):
    package_name = package_name.strip()
    # If it happens to be a URL.
    package_name = package_name.strip('/')
    package_name = package_name.rsplit('/', 1)[-1]
    return package_name

def retry_request(f, tries=5):
    bo = backoff.Linear(m=3, b=3, max=30)
    while tries > 0:
        try:
            return f()
        except requests.exceptions.ConnectionError as exc:
            if tries == 1:
                raise exc
            log.debug(exc)
            time.sleep(bo.next())
        tries -= 1

DOCSTRING = '''
fpk - F-Droid APK downloader
============================

> fpk package_names <flags>

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

--debug:
    Add this flag to see more detailed information.
'''

def fpk_argparse(args):
    destination = pathclass.Path(args.destination)
    destination.assert_is_directory()
    for package in args.packages:
        package = normalize_package_name(package)
        apk_url = retry_request(lambda: get_apk_url(package))

        apk_basename = downloady.basename_from_url(apk_url)
        if args.folders:
            this_dest = destination.with_child(package)
            this_dest.makedirs(exist_ok=True)
        else:
            this_dest = destination
        this_dest = this_dest.with_child(apk_basename)
        if this_dest.exists:
            log.info('%s exists.', this_dest.absolute_path)
            continue

        log.info('Downloading %s', this_dest.absolute_path)
        retry_request(lambda: downloady.download_file(
            apk_url,
            this_dest,
            callback_progress=downloady.Progress2,
            timeout=30,
        ))

def main(argv):
    argv = vlogging.set_level_by_argv(log, argv)

    parser = argparse.ArgumentParser(description=DOCSTRING)

    parser.add_argument('packages', nargs='+')
    parser.add_argument('--folders', action='store_true')
    parser.add_argument('--destination', default='.')
    parser.set_defaults(func=fpk_argparse)

    return betterhelp.single_main(argv, parser, DOCSTRING)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
