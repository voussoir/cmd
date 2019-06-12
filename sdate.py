import datetime
import time

EPOCH = datetime.datetime(
    year=1993,
    month=9,
    day=1,
    tzinfo=datetime.timezone.utc,
)

def sdate():
    (day, hms) = sdate_tuple()
    return f'1993 September {day} {hms}'

def sdate_tuple():
    now = datetime.datetime.now(datetime.timezone.utc)
    diff = now - EPOCH
    day = diff.days + 1
    (minutes, seconds) = divmod(diff.seconds, 60)
    (hours, minutes) = divmod(minutes, 60)
    hms = f'{hours:02}:{minutes:02}:{seconds:02}'
    return (day, hms)

if __name__ == '__main__':
    print(sdate())
