"""Download file.

From: https://github.com/pytorch/vision/blob/934ce3b88c39b94f2851a94d3da89ec91026889b/torchvision/datasets/utils.py

BSD 3-Clause License

Copyright (c) Soumith Chintala 2016,
All rights reserved.
"""

from __future__ import annotations

import itertools
import os
import re
import urllib.request
from typing import Iterator, Optional, Tuple
from urllib.parse import urlparse

import requests
from tqdm import tqdm

__all__ = ['download_url', 'download_file_from_google_drive']

USER_AGENT = 'stomoya/storch'


def _save_response_content(
    content: Iterator[bytes], destination: str, length: int | None = None, verbose: bool = False
) -> None:
    with open(destination, 'wb') as fh, tqdm(total=length, disable=not verbose) as pbar:
        for chunk in content:
            # filter out keep-alive new chunks
            if not chunk:
                continue

            fh.write(chunk)
            pbar.update(len(chunk))


def _urlretrieve(url: str, filename: str, chunk_size: int = 1024 * 32) -> None:
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': USER_AGENT})) as response:
        _save_response_content(iter(lambda: response.read(chunk_size), b''), filename, response.length)


def _get_redirect_url(url, max_hops: int = 3) -> str:
    initial_url = url
    headers = {'Method': 'HEAD', 'User-Agent': USER_AGENT}

    for _ in range(max_hops + 1):
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers)) as response:
            if response.url == url or response.url is None:
                return url
            url = response.url
    raise RecursionError(f'Request to {initial_url} exceeded {max_hops} redirects. The last redirect points to {url}.')


def _get_google_drive_file_id(url: str) -> Optional[str]:
    parts = urlparse(url)

    if re.match(r'(drive|docs)[.]google[.]com', parts.netloc) is None:
        return None

    match = re.match(r'/file/d/(?P<id>[^/]*)', parts.path)
    if match is None:
        return None

    return match.group('id')


def download_url(url: str, root: str, filename: str | None = None, max_redirect_hops: int = 3):
    """Download content of a given url. supports google drive with large files.

    Args:
    ----
        url (str): URL.
        root (str): root directory to save the content.
        filename (str, optional): file name of the saved content. If None base name of the url will be used.
            Default: None.
        max_redirect_hops (int, optional): maximum redirect hops. Default: 3.

    Raises:
    ------
        OSError: download error.

    """
    root = os.path.expanduser(root)
    if filename is None:
        filename = os.path.basename(url)
    output_file = os.path.join(root, filename)

    os.makedirs(root, exist_ok=True)

    url = _get_redirect_url(url, max_hops=max_redirect_hops)
    file_id = _get_google_drive_file_id(url)

    if file_id is not None:
        download_file_from_google_drive(file_id, root, filename)

    try:
        print('Downloading ' + url + ' to ' + output_file)
        _urlretrieve(url, output_file)
    except (urllib.error.URLError, OSError):  # type: ignore[attr-defined]
        if url[:5] == 'https':
            url = url.replace('https:', 'http:')
            print('Failed download. Trying https -> http instead. Downloading ' + url + ' to ' + output_file)
            _urlretrieve(url, output_file)
        else:
            raise


def _extract_gdrive_api_response(response, chunk_size: int = 32 * 1024) -> Tuple[bytes, Iterator[bytes]]:
    content = response.iter_content(chunk_size)
    first_chunk = None
    # filter out keep-alive new chunks
    while not first_chunk:
        first_chunk = next(content)
    content = itertools.chain([first_chunk], content)

    try:
        match = re.search('<title>Google Drive - (?P<api_response>.+?)</title>', first_chunk.decode())
        api_response = match['api_response'] if match is not None else None
    except UnicodeDecodeError:
        api_response = None
    return api_response, content


def download_file_from_google_drive(file_id: str, root: str, filename: Optional[str] = None):
    """Download a Google Drive file from  and place it in root.

    Args:
    ----
        file_id (str): id of file to be downloaded
        root (str): Directory to place downloaded file in
        filename (str, optional): Name to save the file under. If None, use the id of the file.
        md5 (str, optional): MD5 checksum of the download. If None, do not check. Default: None

    """
    # Based on https://stackoverflow.com/questions/38511444/python-download-files-from-google-drive-using-url

    root = os.path.expanduser(root)
    if not filename:
        filename = file_id
    fpath = os.path.join(root, filename)

    os.makedirs(root, exist_ok=True)

    url = 'https://drive.google.com/uc'
    params = dict(id=file_id, export='download')
    with requests.Session() as session:
        response = session.get(url, params=params, stream=True)

        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                token = value
                break
        else:
            api_response, content = _extract_gdrive_api_response(response)
            token = 't' if api_response == 'Virus scan warning' else None

        if token is not None:
            response = session.get(url, params=dict(params, confirm=token), stream=True)
            api_response, content = _extract_gdrive_api_response(response)

        if api_response == 'Quota exceeded':
            raise RuntimeError(
                f'The daily quota of the file {filename} is exceeded and it '
                f"can't be downloaded. This is a limitation of Google Drive "
                f'and can only be overcome by trying again later.'
            )

        _save_response_content(content, fpath)
