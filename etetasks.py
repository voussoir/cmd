'''
I wrote this to make tasks for the tasks.org app with an etebase sync server.

It's not feature comprehensive but it's helpful for bulk task making.

The CLI is not great, it's easier to do python -i pytasks.py and code up
whatever you want.

https://github.com/tasks/tasks
https://github.com/etesync
'''
import argparse
import datetime
import etebase
import sys
import tasks_credentials
import time

from voussoirkit import betterhelp
from voussoirkit import passwordy
from voussoirkit import pipeable
from voussoirkit import timetools
from voussoirkit import vlogging

log = vlogging.getLogger(__name__, '')

PRODID = 'voussoir/pytasks'

client = etebase.Client(tasks_credentials.CLIENT_NAME, tasks_credentials.SERVER)
account = etebase.Account.login(client, tasks_credentials.USERNAME, tasks_credentials.PASSWORD)
collection_manager = account.get_collection_manager()
collections = collection_manager.list('etebase.vtodo', etebase.FetchOptions().limit(500000))
collections = [c for c in collections.data if not c.deleted]

todo = collections[0]
item_manager = collection_manager.get_item_manager(todo)

def make_vcal(text, *, categories=[], due=None):
    now = timetools.now().strftime('%Y%m%dT%H%M%SZ')

    if due is None:
        due = ''
    elif isinstance(due, datetime.date):
        due = 'DUE;VALUE=DATE:' + due.strftime('%Y%m%d')
    elif isinstance(due, datetime.datetime):
        due = 'DUE:' + due.strftime('%Y%m%dT%H%M%S')
    else:
        raise TypeError(due)

    lines = [
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        'PRODID:' + PRODID,
        'BEGIN:VTODO',
        'DTSTAMP:' + now,
        'UID:' + passwordy.random_digits(32),
        due,
        'CREATED:' + now,
        'LAST-MODIFIED:' + now,
        'SUMMARY:' + text,
        ('CATEGORIES:' + ','.join(categories)) if len(categories) > 0 else '',
        'END:VTODO',
        'END:VCALENDAR',
    ]
    lines = [l for l in lines if l]
    vcal = '\r\n'.join(lines) + '\r\n'
    return vcal.encode('utf-8')

def make_item(*args, **kwargs):
    item = item_manager.create({}, make_vcal(*args, **kwargs))
    return item

def publish_items(items):
    if isinstance(items, etebase.Item):
        item_manager.batch([items])
    else:
        item_manager.batch(list(items))

def export_argparse(args):
    items = item_manager.list(etebase.FetchOptions().limit(50000000))
    items = list(items.data)
    for item in items:
        pipeable.stdout(item.content.decode('utf-8'))
        pipeable.stdout()
    return 0

def make_tasks_argparse(args):
    titles = pipeable.input_many(args.titles, strip=True, skip_blank=True)
    items = []
    for title in titles:
        log.info('Creating task %s.', title)
        item = make_item(title)
        items.append(item)
    publish_items(items)
    return 0

@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    ################################################################################################

    p_make_tasks = subparsers.add_parser('make_tasks', aliases=['make-tasks', 'maketasks', 'maketask'])
    p_make_tasks.add_argument('titles', nargs='+')
    p_make_tasks.set_defaults(func=make_tasks_argparse)

    ################################################################################################

    p_export = subparsers.add_parser('export')
    p_export.set_defaults(func=export_argparse)

    return betterhelp.go(parser, argv)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
