"""Notification using LINE notify."""

from __future__ import annotations

import os
import warnings

import requests

LINE_NOTIFY_TOKEN_ENV = 'LINE_NOTIFY_TOKEN'
LINE_NOTIFY_TOKEN = os.environ.get(LINE_NOTIFY_TOKEN_ENV, None)


def send_notify(message: str, image_file: str | None = None, token: str | None = None) -> requests.Response:
    """Send notification using LINE notify.

    Args:
        message (str): The message to send.
        image_file (str | None, optional): path to an image file. Default: None.
        token (str | None, optional): Token. This overwrites the token given by the environment argument.
            Default: None.

    Returns:
        requests.Response: Response object returned by post.

    """
    token = token or LINE_NOTIFY_TOKEN

    if token is None:
        warnings.warn(
            f'A valid token was not provided. Set "{LINE_NOTIFY_TOKEN_ENV}" environment or `token` argument.',
            stacklevel=1,
        )

    api_url = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': f'Bearer {token}'}
    data = {'message': message}

    if image_file is not None:
        with open(image_file, 'rb') as fp:
            files = {'imageFile': fp}
            response = requests.post(api_url, headers=headers, data=data, files=files)

    else:
        response = requests.post(api_url, headers=headers, data=data, files=files)

    return response
