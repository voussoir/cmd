import send2trash
import sys

from voussoirkit import bytestring
from voussoirkit import pathclass
from voussoirkit import pipeable
from voussoirkit import vlogging

log = vlogging.get_logger(__name__, 'recycle')

@vlogging.main_decorator
def main(argv):
    count = 0
    total_bytes = 0
    for path in pathclass.glob_many(pipeable.go(argv, skip_blank=True)):
        pipeable.stdout(path.absolute_path)
        try:
            this_bytes = path.size
            send2trash.send2trash(path)
        except Exception as exc:
            message = f'Recycling {path.absolute_path} caused an exception:\n{exc}'
            log.error(message)
            return 1
        else:
            count += 1
            total_bytes += this_bytes
    log.info(f'Recycled {count} files totaling {bytestring.bytestring(total_bytes)}.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
