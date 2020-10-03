import argparse
import ast
import os
import sys
import threading
import time

from voussoirkit import bytestring
from voussoirkit import clipext
from voussoirkit import downloady


def clean_url_list(urls):
    for url in urls:
        url = url.strip()

        if not url:
            continue

        if url.startswith('#'):
            continue

        yield url

def download_thread(url, filename, *, bytespersecond=None, headers=None, timeout=None):
    print(f' Starting "{filename}"')
    downloady.download_file(url, filename, bytespersecond=bytespersecond, headers=headers, timeout=timeout)
    print(f'+Finished "{filename}"')

def remove_finished(threads):
    return [t for t in threads if t.is_alive()]

def threaded_dl(
        urls,
        thread_count,
        filename_format,
        bytespersecond=None,
        headers=None,
        timeout=None,
    ):
    now = int(time.time())
    threads = []

    bytespersecond_thread = bytespersecond
    if bytespersecond_thread is not None:
        bytespersecond_thread = int(bytespersecond_thread / thread_count)

    if filename_format != os.devnull:
        index_digits = len(str(len(urls)))
        filename_format = filename_format.replace('{index}', '{index:0%0dd}' % index_digits)

        if '{' not in filename_format and len(urls) > 1:
            filename_format += '_{index}'

        if '{extension}' not in filename_format and '{basename}' not in filename_format:
            filename_format += '{extension}'

    for (index, url) in enumerate(clean_url_list(urls)):

        while len(threads) >= thread_count:
            threads = remove_finished(threads)
            time.sleep(0.1)

        basename = downloady.basename_from_url(url)
        extension = os.path.splitext(basename)[1]
        filename = filename_format.format(
            basename=basename,
            ext=extension,
            extension=extension,
            index=index,
            now=now,
        )

        if os.path.exists(filename):
            print(f'Skipping existing file "{filename}"')

        else:
            kwargs = {
                'url': url,
                'bytespersecond': bytespersecond_thread,
                'filename': filename,
                'timeout': timeout,
                'headers': headers,
            }
            t = threading.Thread(target=download_thread, kwargs=kwargs, daemon=True)
            threads.append(t)
            t.start()

    while len(threads) > 0:
        threads = remove_finished(threads)
        print(f'{len(threads)} threads remaining\r', end='', flush=True)
        time.sleep(0.1)

def threaded_dl_argparse(args):
    if os.path.isfile(args.url_file):
        f = open(args.url_file, 'r')
        with f:
            urls = f.read()
    else:
        urls = clipext.resolve(args.url_file)
    urls = urls.replace('\r', '').split('\n')

    headers = args.headers
    if headers is not None:
        if len(headers) == 1 and headers[0].startswith('{'):
            headers = ast.literal_eval(headers[0])
        else:
            keys = headers[::2]
            vals = headers[1::2]
            headers = {key: val for (key, val) in zip(keys, vals)}

    bytespersecond = args.bytespersecond
    if bytespersecond is not None:
        bytespersecond = bytestring.parsebytes(bytespersecond)

    threaded_dl(
        urls,
        bytespersecond=bytespersecond,
        filename_format=args.filename_format,
        headers=headers,
        thread_count=args.thread_count,
        timeout=args.timeout,
    )

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('url_file')
    parser.add_argument('thread_count', type=int)
    parser.add_argument('filename_format', nargs='?', default='{now}_{index}_{basename}')
    parser.add_argument('--bytespersecond', dest='bytespersecond', default=None)
    parser.add_argument('--timeout', dest='timeout', default=15)
    parser.add_argument('--headers', dest='headers', nargs='+', default=None)
    parser.set_defaults(func=threaded_dl_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
