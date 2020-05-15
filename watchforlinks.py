import pyperclip
import sys
import time

from voussoirkit import passwordy

def loop_once():
    try:
        text = pyperclip.paste()
    except Exception:
        return

    if '\n' in text:
        return

    if 'http://' in text or 'https://' in text:
        fn = passwordy.urandom_hex(12) + '.generic'
        pyperclip.copy('')
        print(fn, text)
        h = open(fn, 'w', encoding='utf-8')
        h.write(text)
        h.close()

def loop_forever():
    while True:
        loop_once()
        time.sleep(1)

def main(argv):
    try:
        loop_forever()
    except KeyboardInterrupt:
        pass

    return 0

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
