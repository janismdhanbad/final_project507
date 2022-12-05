import urllib.request as libreq
import requests

import urllib.request as libreq
link = 'http://export.arxiv.org/api/query?search_query=all:electron&start=0&max_results=1'
requests.get(link)
# with libreq.urlopen('http://export.arxiv.org/api/query?search_query=all:electron&start=0&max_results=1') as url:
#     r = url.read()
# print(r)

