import math
import sys

from voussoirkit import pipeable


def hms_to_seconds(hms):
    '''
    Convert hh:mm:ss string to an integer seconds.
    '''
    hms = hms.split(':')
    seconds = 0
    if len(hms) == 3:
        seconds += int(hms[0]) * 3600
        hms.pop(0)
    if len(hms) == 2:
        seconds += int(hms[0]) * 60
        hms.pop(0)
    if len(hms) == 1:
        seconds += float(hms[0])
    return seconds

def seconds_to_hms(seconds):
    '''
    Convert integer number of seconds to an hh:mm:ss string.
    Only the necessary fields are used.
    '''
    (minutes, seconds) = divmod(seconds, 60)
    (hours, minutes) = divmod(minutes, 60)

    parts = []
    if hours:
        parts.append(f'{int(hours):02d}')
    if minutes:
        parts.append(f'{int(minutes):02d}')
    if seconds == int(seconds):
        parts.append(f'{int(seconds):02d}')
    else:
        parts.append(f'{seconds:0.3f}')
    hms = ':'.join(parts)

    return hms

def main(args):
    for line in pipeable.go(args, strip=True, skip_blank=True):
        if ':' in line:
            line = hms_to_seconds(line)
        else:
            line = float(line)
            if line > 60:
                line = seconds_to_hms(line)

        pipeable.output(f'{line}')


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
