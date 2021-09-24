'''
lint_argparse_returns
=====================
'''
import ast
import argparse
import sys

from voussoirkit import pathclass
from voussoirkit import vlogging

log = vlogging.getLogger(__name__, 'lint_argparse_returns')

@vlogging.main_decorator
def main(argv):
    return_status = 0

    files = pathclass.glob('*.py')
    files = (f for f in files if f.is_file)
    for file in files:
        no_py = file.replace_extension('').basename
        text = file.open('r', encoding='utf-8').read()
        try:
            tree = ast.parse(text)
        except Exception:
            log.error('%s failed to parse.', file.absolute_path)
            return_status = 1
            continue
        functions = [f for f in tree.body if isinstance(f, ast.FunctionDef)]
        functions = [f for f in functions if f.name.endswith('_argparse') or f.name == 'main']
        for function in functions:
            returns = [node for node in ast.walk(function) if isinstance(node, ast.Return)]

            if not returns:
                log.warning('%s.%s has no return.', no_py, function.name)
                return_status = 1

            for ret in returns:
                source = ast.get_source_segment(text, ret.value)
                log.info('%s.%s returns %s.', no_py, function.name, source)

    return return_status

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
