import socket
import sqlite3
import sys
import time

from voussoirkit import hms
from voussoirkit import threadpool
from voussoirkit import vlogging

log = vlogging.getLogger(__name__, 'internetcheck')
vlogging.getLogger('threadpool').setLevel(vlogging.WARNING)

sql = sqlite3.connect('internetcheck.db')
cur = sql.cursor()

DB_INIT = '''
BEGIN;
CREATE TABLE IF NOT EXISTS outages(
    timestamp INT PRIMARY KEY,
    human TEXT,
    lan_ok INT,
    dns_ok INT,
    ip_ok INT,
    duration INT
);
COMMIT;
'''
cur.executescript(DB_INIT)

down = False
outage_started = None
thread_pool = threadpool.ThreadPool(10)

def percentage(items):
    trues = sum(bool(i) for i in items)
    return trues / len(items)

def ping_lan():
    ip = '192.168.1.1'
    log.debug('Checking LAN at %s.', ip)
    try:
        socket.setdefaulttimeout(1)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((ip, 80))
        return True
    except socket.error:
        return False

def check_dns():
    def check(domain):
        log.debug('Checking DNS for %s.', domain)
        try:
            socket.getaddrinfo(domain, 53)
            return True
        except socket.gaierror:
            return False
    names = [
        'amazon.com',
        'bing.com',
        'comcast.com',
        'frontier.com',
        'google.com',
        'microsoft.com',
        'netflix.com',
        'reddit.com',
        'spectrum.com',
        'youtube.com',
    ]
    thread_pool.pause()
    jobs = [{'function': check, 'args': [name]} for name in names]
    thread_pool.add_many(jobs)
    checks = [job.value for job in thread_pool.result_generator()]
    return percentage(checks)

def check_ip():
    def check(ip):
        log.debug('Checking IP %s.', ip)
        try:
            socket.setdefaulttimeout(2)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(('104.43.253.214', 80))
            return True
        except socket.error:
            return False
    ips = [
        '104.43.253.214',
        '13.107.21.200',
        '13.77.161.179',
        '142.136.81.136',
        '151.101.1.140',
        '172.217.11.174',
        '172.217.11.78',
        '176.32.103.205',
        '35.165.194.49',
        '69.252.80.75',
    ]
    thread_pool.pause()
    jobs = [{'function': check, 'args': [ip]} for ip in ips]
    thread_pool.add_many(jobs)
    checks = [job.value for job in thread_pool.result_generator()]
    return percentage(checks)

def set_down(lan_ok, dns_ok, ip_ok):
    global down
    global outage_started
    if down:
        duration = int(time.time() - outage_started)
        duration = hms.seconds_to_hms(duration)
        print(f'Still down for {duration}.')
        return
    print('Starting down timer.')
    down = True
    outage_started = int(time.time())
    human = time.strftime('%Y-%m-%d %H:%M:%S')
    cur.execute(
        'INSERT INTO outages VALUES(?, ?, ?, ?, ?, ?)',
        [outage_started, human, lan_ok, dns_ok, ip_ok, None]
    )
    sql.commit()

def end_down():
    global down
    global outage_started
    if not down:
        return
    duration = int(time.time() - outage_started)
    cur.execute('UPDATE outages SET duration = ? WHERE timestamp == ?', [duration, outage_started])
    sql.commit()
    down = False
    outage_started = None

def check_forever():
    while True:
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        lan_ok = int(ping_lan())
        dns_stat = check_dns()
        ip_stat = check_ip()
        message = f'{now}, LAN={lan_ok}, DNS={dns_stat:0.2f}, IP={ip_stat:0.2f}'
        dns_ok = dns_stat > 0.75
        ip_ok = ip_stat > 0.75
        if not (lan_ok and dns_ok and ip_ok):
            print(message, end=', ')
            set_down(lan_ok, dns_ok, ip_ok)
        else:
            print(message + '\r', end='', flush=True)
            end_down()

        if down:
            time.sleep(1)
        else:
            time.sleep(20)

def main(argv):
    argv = vlogging.main_level_by_argv(argv)

    try:
        check_forever()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
