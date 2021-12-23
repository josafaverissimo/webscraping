from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
from time import sleep
from random import randrange
import json


def get_page(url):
    response = perform_request_and_get_response(url)

    if response is None:
        return None

    html = BeautifulSoup(response.read(), 'html.parser')

    return html


def get_pages_from_urls(urls, callback):
    pages = []

    for url in urls:
        page = get_page(url)

        if page is not None:
            page = callback(page)
            pages.append(page)

    return pages


def get_data_from_json_api(url):
    response = perform_request_and_get_response(url)

    if response is None:
        return None

    response = json.loads(response.read())

    return response


def perform_request_and_get_response(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US'
    }

    response = None

    try:
        request = Request(url, headers=headers)

        sleep(randrange(1, 10))

        response = urlopen(request)

        print(f"[*]: {url}")
    except HTTPError as e:
        print(e)
        print(f"[x] Failed to get: {url}")
    except URLError as e:
        print(e)
        print(f"[x] Failed to get: {url}")
    except:
        print(f'[x] failed to get: {url}')
    finally:
        return response
