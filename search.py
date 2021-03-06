import argparse
import itertools
import os
import re
import stat
import sys
import traceback
try:
    import winshell
except ImportError:
    winshell = None

from voussoirkit import clipext
from voussoirkit import expressionmatch
from voussoirkit import pathclass
from voussoirkit import pipeable
from voussoirkit import safeprint
from voussoirkit import spinal
from voussoirkit import winglob

# Thanks georg
# http://stackoverflow.com/a/13443424
STDIN_MODE = os.fstat(sys.stdin.fileno()).st_mode
if stat.S_ISFIFO(STDIN_MODE):
    STDIN_MODE = 'pipe'
else:
    STDIN_MODE = 'terminal'

class NoTerms(Exception):
    pass

class HeaderedText:
    def __init__(self, header, text):
        self.header = header
        self.text = text

    @property
    def with_header(self):
        return f'{self.header}: {self.text}'


def all_terms_match(search_text, terms, match_function):
    matches = (
        (not terms['yes_all'] or all(match_function(search_text, term) for term in terms['yes_all'])) and
        (not terms['yes_any'] or any(match_function(search_text, term) for term in terms['yes_any'])) and
        (not terms['not_all'] or not all(match_function(search_text, term) for term in terms['not_all'])) and
        (not terms['not_any'] or not any(match_function(search_text, term) for term in terms['not_any']))
    )
    return matches

def search_contents_generic(filepath, content_args):
    try:
        with filepath.open('r') as handle:
            text = handle.read()
    except UnicodeDecodeError:
        try:
            with filepath.open('r', encoding='utf-8') as handle:
                text = handle.read()
        except UnicodeDecodeError:
            #safeprint.safeprint(filepath.absolute_path)
            #traceback.print_exc()
            return
    except Exception:
        safeprint.safeprint(filepath.absolute_path)
        traceback.print_exc()
        return

    content_args['text'] = text
    content_args['line_numbers'] = True

    results = search(**content_args)
    results = list(results)
    if not results:
        return

    yield filepath.absolute_path
    yield from results
    yield ''

def search_contents_windows_lnk(filepath, content_args):
    try:
        shortcut = winshell.Shortcut(filepath.absolute_path)
    except Exception:
        return

    text = [
        HeaderedText('Target', shortcut.path),
        HeaderedText('Arguments', shortcut.arguments),
        HeaderedText('Start In', shortcut.working_directory),
        HeaderedText('Comment', shortcut.description),
    ]
    content_args['text'] = text

    results = search(**content_args)
    results = list(results)
    if not results:
        return

    yield filepath.absolute_path
    yield from results
    yield ''

def search(
        *,
        yes_all=None,
        yes_any=None,
        not_all=None,
        not_any=None,
        case_sensitive=False,
        content_args=None,
        do_expression=False,
        do_glob=False,
        do_regex=False,
        do_strip=False,
        line_numbers=False,
        local_only=False,
        only_dirs=False,
        only_files=False,
        root_path='.',
        text=None,
    ):
    terms = {
        'yes_all': yes_all,
        'yes_any': yes_any,
        'not_all': not_all,
        'not_any': not_any
    }
    terms = {k: ([v] if isinstance(v, str) else v or []) for (k, v) in terms.items()}
    #print(terms, content_args)

    do_plain = not (do_glob or do_regex)

    if all(v == [] for v in terms.values()) and not content_args:
        raise NoTerms('No terms supplied')

    def term_matches(line, term):
        if not case_sensitive:
            line = line.lower()

        if do_expression:
            return term.evaluate(line)

        return (
            (do_plain and term in line) or
            (do_regex and re.search(term, line)) or
            (do_glob and winglob.fnmatch(line, term))
        )

    if do_expression:
        # The value still needs to be a list so the upcoming any() / all()
        # receives an iterable as it expects. It just happens to be 1 tree.
        trees = {}
        for (term_type, term_expression) in terms.items():
            if term_expression == []:
                trees[term_type] = []
                continue
            tree = ' '.join(term_expression)
            tree = expressionmatch.ExpressionTree.parse(tree)
            if not case_sensitive:
                tree.map(str.lower)
            trees[term_type] = [tree]
        terms = trees

    elif not case_sensitive:
        terms = {k: [x.lower() for x in v] for (k, v) in terms.items()}

    if text is None:
        search_objects = spinal.walk_generator(
            root_path,
            recurse=not local_only,
            yield_directories=True,
        )
    elif isinstance(text, (list, tuple)):
        search_objects = text
    else:
        search_objects = text.splitlines()

    for (index, search_object) in enumerate(search_objects):
        # if index % 10 == 0:
        #     print(index, end='\r', flush=True)
        if isinstance(search_object, pathclass.Path):
            if only_files and not search_object.is_file:
                continue
            if only_dirs and not search_object.is_dir:
                continue
            search_text = search_object.basename
            result_text = search_object.absolute_path
        elif isinstance(search_object, HeaderedText):
            search_text = search_object.text
            result_text = search_object.with_header
        else:
            search_text = search_object
            result_text = search_object

        if not all_terms_match(search_text, terms, term_matches):
            continue

        if do_strip:
            result_text = result_text.strip()

        if line_numbers:
            result_text = f'{index+1:>4} | {result_text}'

        if not content_args:
            yield result_text
            continue

        filepath = pathclass.Path(search_object)
        if not filepath.is_file:
            continue

        if filepath.extension == 'lnk' and winshell:
            yield from search_contents_windows_lnk(filepath, content_args)
        else:
            yield from search_contents_generic(filepath, content_args)

def argparse_to_dict(args):
    text = args.text
    if text is not None:
        text = clipext.resolve(text)
    elif STDIN_MODE == 'pipe':
        text = clipext.resolve('!i')

    if hasattr(args, 'content_args') and args.content_args is not None:
        content_args = argparse_to_dict(args.content_args)
    else:
        content_args = None

    return {
        'yes_all': args.yes_all_1 + args.yes_all_2,
        'yes_any': args.yes_any,
        'not_all': args.not_all,
        'not_any': args.not_any,
        'case_sensitive': args.case_sensitive,
        'content_args': content_args,
        'do_expression': args.do_expression,
        'do_glob': args.do_glob,
        'do_regex': args.do_regex,
        'do_strip': args.do_strip,
        'local_only': args.local_only,
        'line_numbers': args.line_numbers,
        'only_dirs': args.only_dirs,
        'only_files': args.only_files,
        'text': text,
    }

def _search_argparse(args):
    generator = search(**argparse_to_dict(args))
    result_count = 0
    for result in generator:
        safeprint.safeprint(result)
        result_count += 1
    if args.show_count:
        print('%d items.' % result_count)

@pipeable.ctrlc_return1
def search_argparse(args):
    try:
        return _search_argparse(args)
    except NoTerms:
        print('You did not supply any search terms.')
        return 1

def main(argv):
    parser = argparse.ArgumentParser()

    # The padding is inserted to guarantee that --content is not the first
    # argument. Because if it were, we wouldn't know if we have
    # [pre, '--content'] or ['--content', post], etc. and I don't want to
    # actually check the values.
    argv.insert(0, 'padding')
    grouper = itertools.groupby(argv, lambda x: x == '--content')
    halves = [list(group) for (key, group) in grouper]
    # halves looks like [pre, '--content', post]
    name_args = halves[0]
    # Pop the padding
    name_args.pop(0)
    content_args = [item for chunk in halves[2:] for item in chunk]

    # argparse doesn't work well when an argument is both positional and
    # named, so both of these yes_all will be combined into a single list
    # during the gateway function.
    parser.add_argument('yes_all_1', nargs='*', default=None)
    parser.add_argument('--all', dest='yes_all_2', nargs='+', default=[])
    parser.add_argument('--any', dest='yes_any', nargs='+', default=[])
    parser.add_argument('--not_all', '--not-all', dest='not_all', nargs='+', default=[])
    parser.add_argument('--not_any', '--not-any', dest='not_any', nargs='+', default=[])

    parser.add_argument('--strip', dest='do_strip', action='store_true')
    parser.add_argument('--case', dest='case_sensitive', action='store_true')
    parser.add_argument('--content', dest='do_content', action='store_true')
    parser.add_argument('--count', dest='show_count', action='store_true')
    parser.add_argument('--expression', dest='do_expression', action='store_true')
    parser.add_argument('--glob', dest='do_glob', action='store_true')
    parser.add_argument('--line_numbers', '--line-numbers', dest='line_numbers', action='store_true')
    parser.add_argument('--local', dest='local_only', action='store_true')
    parser.add_argument('--regex', dest='do_regex', action='store_true')
    parser.add_argument('--text', dest='text', default=None)
    parser.add_argument('--dirs', '--folders', dest='only_dirs', action='store_true')
    parser.add_argument('--files', dest='only_files', action='store_true')
    parser.set_defaults(func=search_argparse)

    args = parser.parse_args(name_args)
    if content_args:
        args.content_args = parser.parse_args(content_args)
    else:
        args.content_args = None

    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
