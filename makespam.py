import time
import textwrap
import re
import html
import pyperclip

TEMPLATE = '''
    <article>
{selectheaders}
        <details>
        <summary>Headers</summary>
        <pre>
{headers}
        </pre>
        </details>

        <hr/>

{body}
    </article>
'''


print('Copy the body...')
pyperclip.copy('')
while pyperclip.paste() == '':
    time.sleep(0.5)
body = html.escape(pyperclip.paste())
body = body.replace('\r', '')
body = [line.strip() for line in body.splitlines()]
body = [line for line in body if line]
body = ['<p>' + line + '</p>' for line in body]
body = '\n'.join(body)
body = textwrap.indent(body, '        ')

print('Copy the headers...')
pyperclip.copy('')
while pyperclip.paste() == '':
    time.sleep(0.5)
headers = html.escape(pyperclip.paste())
headers = headers.replace('\r', '')
headers = [line.rstrip() for line in headers.splitlines()]
headers = [line for line in headers if line]
headers = '\n'.join(headers)

keyed = {}
for line in headers.splitlines():
    key = re.search(r'^([A-Za-z\-]+): ', line, flags=re.MULTILINE)
    if key is None:
        continue
    key = key.group(1)
    line = line.replace(key + ':', '<p><b>' + key + '</b>:')
    keyed[key] = line

selectheaders = [
    keyed.get('From'),
    keyed.get('Reply-To'),
    keyed.get('Return-Path'),
    keyed.get('To'),
    keyed.get('Bcc'),
    keyed.get('Subject'),
    keyed.get('Date'),
]
selectheaders = [s for s in selectheaders if s]
selectheaders = '\n'.join(selectheaders)
selectheaders = textwrap.indent(selectheaders, '        ')

spam = TEMPLATE.format(body=body, headers=headers, selectheaders=selectheaders)
print(spam)
pyperclip.copy(spam)