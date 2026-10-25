"""Shared, standard-library helpers for read-only blog maintenance."""
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import re

ROOT = Path(__file__).resolve().parents[1]

def fetch(url, timeout=20):
    if urlsplit(url).scheme not in ('http', 'https'):
        raise ValueError('Only HTTP(S) URLs are supported')
    request = Request(url, headers={'User-Agent': 'JamesCullimoreWebsiteLinkCheck/1.0 (+https://jamescullimore.dev)'})
    try:
        response = urlopen(request, timeout=timeout)
    except HTTPError as error:
        response = error
    with response:
        body = response.read(8 * 1024 * 1024 + 1)
        if len(body) > 8 * 1024 * 1024:
            raise ValueError('Response exceeds 8 MiB; review manually')
        return response.status, response.geturl(), body.decode('utf-8', errors='replace')

def post_id(url):
    match = re.search(r'(?:-|/)([a-f0-9]{12})(?:[/?#]|$)', url)
    return match.group(1) if match else None

def clean_url(url):
    parts = urlsplit(url)
    return parts._replace(query='', fragment='').geturl()
