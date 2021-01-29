import argparse
import flask; from flask import request
import os
import pyperclip
import sys

from voussoirkit import vlogging

log = vlogging.getLogger(__name__, 'heresmyclipboard')

site = flask.Flask(__name__)

@site.route('/')
def root():
    clip = pyperclip.paste()
    template = '''
    <html>
    <body>
    <pre>
    {{clip}}
    </pre>
    </body>
    </html>
    '''
    return flask.render_template_string(template, clip=clip)

def heresmyclipboard_argparse(args):
    log.info(f'Starting server on port {args.port}, pid={os.getpid()}')
    site.run(host='0.0.0.0', port=args.port)

def main(argv):
    argv = vlogging.set_level_by_argv(log, argv)

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('port', nargs='?', type=int, default=4848)
    parser.set_defaults(func=heresmyclipboard_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
