import argparse
import io
import json
import os
import requests
import sys
import time
import traceback
import zipfile

from voussoirkit import interactive
from voussoirkit import operatornotify
from voussoirkit import pipeable
from voussoirkit import vlogging

log = vlogging.getLogger(__name__, 'getcrx')

FILENAME_BADCHARS = '\\/:*?<>|"'

WEBSTORE_URL = 'https://chrome.google.com/webstore/detail/{extension_id}'
CRX_URL = 'https://clients2.google.com/service/update2/crx?response=redirect&prodversion=131.0.6167.161&acceptformat=crx2,crx3&x=id%3D{extension_id}%26uc'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'

session = requests.Session()
session.headers={'User-Agent': USER_AGENT}

def sanitize_filename(name):
    for c in FILENAME_BADCHARS:
        name = name.replace(c, '-')
    return name

def get_webstore_name_version(extension_id):
    url = WEBSTORE_URL.format(extension_id=extension_id)
    response = session.get(url, timeout=60)
    response.raise_for_status()

    try:
        name = response.text
        name = name.split('meta property="og:title" content="')[1]
        name = name.split('"')[0]
    except IndexError:
        name = None

    try:
        version = response.text
        version = version.split('meta itemprop="version" content="')[1]
        version = version.split('"')[0]
    except IndexError:
        version = None

    return (name, version)

def get_crx_name_version(crx_bytes):
    crx_handle = io.BytesIO(crx_bytes)
    crx_archive = zipfile.ZipFile(crx_handle)
    manifest = json.loads(crx_archive.read('manifest.json'))
    name = manifest.get('name', None)
    version = manifest.get('version', None)
    return (name, version)

def get_crx(extension_id):
    url = CRX_URL.format(extension_id=extension_id)
    response = session.get(url)
    response.raise_for_status()
    return response.content

def download_crx(extension_id, auto_overwrite=None):
    log.info('Checking %s.', extension_id)
    (name, version) = get_webstore_name_version(extension_id)

    crx_bytes = get_crx(extension_id)

    if name is None or version is None:
        (crx_name, crx_ver) = get_crx_name_version(crx_bytes)
        name = name or crx_name
        version = version or crx_ver

    name = name or extension_id
    version = version or time.strftime('%Y-%m-%d')

    crx_filename = '{name} ({id}) [{version}]'
    crx_filename = crx_filename.format(
        name=name,
        id=extension_id,
        version=version,
    )

    if not crx_filename.endswith('.crx'):
        crx_filename += '.crx'

    crx_filename = sanitize_filename(crx_filename)
    if os.path.isfile(crx_filename):
        if auto_overwrite is True:
            permission = True
        if auto_overwrite is None:
            message = f'"{crx_filename}" already exists. Overwrite?'
            permission = interactive.getpermission(message)
        else:
            permission = False
    else:
        permission = True

    if permission:
        crx_handle = open(crx_filename, 'wb')
        crx_handle.write(crx_bytes)
        log.info(f'Downloaded "{crx_filename}".')

def getcrx_argparse(args):
    extension_ids = []

    if len(args.extension_ids) == 1:
        extension_ids.extend(pipeable.input(args.extension_ids[0]))

    elif args.extension_ids:
        extension_ids.extend(args.extension_ids)

    if args.file:
        with open(args.file, 'r') as handle:
            lines = handle.readlines()
        extension_ids.extend(lines)

    extension_ids = [x for x in extension_ids if not x.startswith('#')]
    extension_ids = [x.rsplit('/', 1)[-1].strip() for x in extension_ids]

    if args.overwrite and not args.dont_overwrite:
        auto_overwrite = True
    elif args.dont_overwrite and not args.overwrite:
        auto_overwrite = False
    else:
        auto_overwrite = None

    return_status = 0
    for extension_id in extension_ids:
        try:
            download_crx(extension_id, auto_overwrite=auto_overwrite)
        except Exception:
            if args.fail_early:
                raise
            else:
                log.error(traceback.format_exc())
                pipeable.stderr('Resuming...')
                return_status = 1
    return return_status

@operatornotify.main_decorator(subject='getcrx')
@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('extension_ids', nargs='*', default=None)
    parser.add_argument('--file', default=None)
    parser.add_argument('--fail_early', '--fail-early', action='store_true')
    parser.add_argument('--overwrite', action='store_true')
    parser.add_argument('--dont_overwrite', '--dont-overwrite', action='store_true')
    parser.set_defaults(func=getcrx_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
