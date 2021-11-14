from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US'
}

def get_page(url):
    html = None

    try:
        request = Request(url, headers=headers)
        response = urlopen(request).read()
        html = BeautifulSoup(response, 'html.parser')    
    except HTTPError as e:
        print(e)
    except URLError as e:
        print(e)
    finally:
        print(f"success to get: {url}")
        return html