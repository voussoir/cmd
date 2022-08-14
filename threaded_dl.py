import argparse
import ast
import os
import shutil
import sys
import threading
import time

from voussoirkit import betterhelp
from voussoirkit import bytestring
from voussoirkit import downloady
from voussoirkit import pathclass
from voussoirkit import pipeable
from voussoirkit import ratelimiter
from voussoirkit import ratemeter
from voussoirkit import threadpool
from voussoirkit import vlogging

log = vlogging.getLogger(__name__, 'threaded_dl')
downloady.log.setLevel(vlogging.WARNING)

def clean_url_list(urls):
    for url in urls:
        if isinstance(url, (tuple, list)):
            (url, filename) = url
        else:
            filename = None
        url = url.strip()

        if not url:
            continue

        if url.startswith('#'):
            continue

        if filename:
            yield (url, filename)
        else:
            yield url

def download_job(
        url,
        filename,
        *,
        bytespersecond=None,
        headers=None,
        meter=None,
        timeout=None,
    ):
    log.info(f'Starting "{filename}"')
    downloady.download_file(
        url,
        filename,
        bytespersecond=bytespersecond,
        headers=headers,
        ratemeter=meter,
        timeout=timeout,
    )
    log.info(f'Finished "{filename}"')

def normalize_headers(headers):
    if headers is None:
        return {}

    if not headers:
        return {}

    if isinstance(headers, dict):
        return headers

    if isinstance(headers, list) and len(headers) == 1:
        headers = headers[0]

    if isinstance(headers, (list, tuple)):
        keys = headers[::2]
        vals = headers[1::2]
        return {key: val for (key, val) in zip(keys, vals)}

    if isinstance(headers, str) and os.path.isfile(headers):
        headers = pathclass.Path(headers).readlines('r', encoding='utf-8')

    if isinstance(headers, str):
        if headers.startswith('{'):
            return ast.literal_eval(headers)
        else:
            lines = [line for line in headers.splitlines() if line.strip()]
            pairs = [line.strip().split(': ', 1) for line in lines]
            return {key: value for (key, value) in pairs}

    return headers

def prepare_urls_filenames(urls, filename_format):
    now = int(time.time())

    if os.path.normcase(filename_format) != os.devnull:
        index_digits = len(str(len(urls)))
        filename_format = filename_format.replace('{index}', '{index:0%0dd}' % index_digits)

        if '{' not in filename_format and len(urls) > 1:
            filename_format += '_{index}'

        if '{extension}' not in filename_format and '{basename}' not in filename_format:
            filename_format += '{extension}'

    urls_filenames = []

    for (index, url) in enumerate(clean_url_list(urls)):
        if isinstance(url, (tuple, list)):
            (url, filename) = url
        else:
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
            log.info(f'Skipping existing file "{filename}"')
            continue

        urls_filenames.append((url, filename))

    return urls_filenames

def threaded_dl(
        urls,
        thread_count,
        filename_format,
        bytespersecond=None,
        headers=None,
        timeout=None,
    ):
    urls_filenames = prepare_urls_filenames(urls, filename_format)

    if not urls_filenames:
        return

    if bytespersecond is not None:
        # It is important that we convert this to a Ratelimter now instead of
        # passing the user's integer to downloady, because we want all threads
        # to share a single limiter instance instead of each creating their
        # own by the integer.
        bytespersecond = ratelimiter.Ratelimiter(bytespersecond)

    meter = ratemeter.RateMeter(span=5)

    pool = threadpool.ThreadPool(thread_count, paused=True)

    ui_stop_event = threading.Event()
    ui_kwargs = {
        'meter': meter,
        'stop_event': ui_stop_event,
        'pool': pool,
    }
    ui_thread = threading.Thread(target=ui_thread_func, kwargs=ui_kwargs, daemon=True)
    ui_thread.start()

    kwargss = []
    for (url, filename) in urls_filenames:
        kwargs = {
            'function': download_job,
            'kwargs': {
                'bytespersecond': bytespersecond,
                'filename': filename,
                'headers': headers,
                'meter': meter,
                'timeout': timeout,
                'url': url,
            }
        }
        kwargss.append(kwargs)
    pool.add_many(kwargss)

    for job in pool.result_generator():
        if job.exception:
            ui_stop_event.set()
            ui_thread.join()
            raise job.exception

    ui_stop_event.set()
    ui_thread.join()

def ui_thread_func(meter, pool, stop_event):
    if pipeable.stdout_pipe():
        return

    while not stop_event.is_set():
        width = shutil.get_terminal_size().columns
        speed = meter.report()[2]
        message = f'{bytestring.bytestring(speed)}/s | {pool.running_count} threads'
        spaces = ' ' * (width - len(message) - 1)
        pipeable.stderr(message + spaces, end='\r')

        stop_event.wait(timeout=0.5)

def threaded_dl_argparse(args):
    urls = pipeable.input(args.url_file, read_files=True, skip_blank=True, strip=True)
    urls = [u.split(' ', 1) if ' ' in u else u for u in urls]

    headers = normalize_headers(args.headers)

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

    return 0

@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'url_file',
        metavar='links',
        help='''
        The name of a file containing links to download, one per line.
        Uses pipeable to support !c clipboard, !i stdin lines of urls.
        ''',
    )
    parser.add_argument(
        'thread_count',
        type=int,
        help='''
        Integer number of threads to use for downloading.
        ''',
    )
    parser.add_argument(
        'filename_format',
        nargs='?',
        type=str,
        default='{now}_{index}_{basename}',
        help='''
        A string that controls the names of the downloaded files. Uses Python's
        brace-style formatting. Available formatters are:
        - {basename}: The name of the file as indicated by the URL.
          E.g. example.com/image.jpg -> image.jpg
        - {extension}: The extension of the file as indicated by the URL, including
          the dot. E.g. example.com/image.jpg -> .jpg
        - {index}: The index of this URL within the sequence of all downloaded URLs.
          Starts from 0.
        - {now}: The unix timestamp at which this download job was started. It might
          be ugly but at least it's unambiguous when doing multiple download batches
          with similar filenames.
        ''',
    )
    parser.add_argument(
        '--bytespersecond',
        default=None,
        help='''
        Limit the overall download speed to X bytes per second. Uses
        bytestring.parsebytes to support strings like "1m", "500k", "2 mb", etc.
        ''',
    )
    parser.add_argument(
        '--timeout',
        default=15,
        help='''
        Integer number of seconds to use as HTTP request timeout for each download.
        ''',
    )
    parser.add_argument(
        '--headers', nargs='+', default=None,
    )
    parser.set_defaults(func=threaded_dl_argparse)

    return betterhelp.go(parser, argv)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
