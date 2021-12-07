'''
threaded_dl
===========

> threaded_dl links thread_count filename_format <flags>

links:
    The name of a file containing links to download, one per line.
    Uses pipeable to support !c clipboard, !i stdin lines of urls.

thread_count:
    Integer number of threads to use for downloading.

filename_format:
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

flags:
--bytespersecond X:
    Limit the overall download speed to X bytes per second. Uses
    bytestring.parsebytes to support strings like "1m", "500k", "2 mb", etc.

--headers X:
    ;

--timeout X:
    Integer number of seconds to use as HTTP request timeout for each download.
'''
import argparse
import ast
import os
import queue
import shutil
import sys
import threading
import time

from voussoirkit import betterhelp
from voussoirkit import bytestring
from voussoirkit import downloady
from voussoirkit import pipeable
from voussoirkit import ratelimiter
from voussoirkit import ratemeter
from voussoirkit import sentinel
from voussoirkit import threadpool
from voussoirkit import vlogging

log = vlogging.getLogger(__name__, 'threaded_dl')
downloady.log.setLevel(vlogging.WARNING)

THREAD_FINISHED = sentinel.Sentinel('thread finished')

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
    if pipeable.OUT_PIPE:
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

    return 0

@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('url_file')
    parser.add_argument('thread_count', type=int)
    parser.add_argument('filename_format', nargs='?', default='{now}_{index}_{basename}')
    parser.add_argument('--bytespersecond', default=None)
    parser.add_argument('--timeout', default=15)
    parser.add_argument('--headers', nargs='+', default=None)
    parser.set_defaults(func=threaded_dl_argparse)

    return betterhelp.single_main(argv, parser, __doc__)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
