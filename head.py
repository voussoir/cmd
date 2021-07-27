'''
Perform a HEAD request and print the results.
'''
import sys
import json
import requests

from voussoirkit import pipeable

urls = pipeable.input(sys.argv[1], skip_blank=True, strip=True)
for url in urls:
    page = requests.head(url)
    headers = dict(page.headers)
    headers = json.dumps(headers, indent=4, sort_keys=True)
    print(page)
    print(headers)
