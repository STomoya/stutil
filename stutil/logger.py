"""logfger."""

from __future__ import annotations

import logging
import sys
from contextlib import contextmanager
from typing import Union

__all__ = ['open_redirect_std_stream', 'close_redirect_std_stream', 'redirect_stds', 'get_logger']


_stream = None


def open_redirect_std_stream(filename: str | None = None, mode: str = 'a') -> 'RedirectStdStream':
    """Open a stream that redirect stderr to stdout and optionally print to file.

    Args:
    ----
        filename (str, optional): File name to print to. Default: None.
        mode (str, optional): File writinf mode. Default: 'a'.

    Returns:
    -------
        RedirectStdStream: stream

    """
    global _stream  # noqa: PLW0603
    if _stream is None:
        _stream = RedirectStdStream(filename, mode)
    return _stream


def close_redirect_std_stream():
    """Close the stream opened by "open_redirect_std_stream."""
    global _stream  # noqa: PLW0603
    if _stream is not None:
        _stream.close()
    _stream = None


@contextmanager
def redirect_stds(filename: str | None = None, mode: str = 'a'):
    """Inside this context manager the stderr will be redirected to stdout, and optionally prints the outputs to a file.

    This stream only lives within the "with" statement.

    Args:
    ----
        filename (str, optional): File name to print to. Default: None.
        mode (str, optional): File writinf mode. Default: 'a'.

    Examples:
    --------
        >>> with redirect_stds('log.log'):
        >>>     print('stdout will be saved to "log.log"')
        >>>     warnings.warn('stderr will also be saved to "log.log"')

    """
    open_redirect_std_stream(filename, mode)
    yield
    close_redirect_std_stream()


class RedirectStdStream(object):
    """Redirect stderr to stdout, optionally print stdout to a file.

    from: https://github.com/NVlabs/stylegan3/blob/583f2bdd139e014716fc279f23d362959bcc0f39/dnnlib/util.py#L56-L112
    """

    def __init__(self, file_name: str | None = None, file_mode: str = 'a', should_flush: bool = True):
        self.file = None

        if file_name is not None:
            self.file = open(file_name, file_mode)  # noqa: SIM115

        self.should_flush = should_flush
        self.stdout = sys.stdout
        self.stderr = sys.stderr

        sys.stdout = self
        sys.stderr = self

    def write(self, text: Union[str, bytes]) -> None:
        """Write text to stdout (and a file) and optionally flush.

        Args:
        ----
            text (Union[str, bytes]): Text to write.

        """
        if isinstance(text, bytes):
            text = text.decode()
        if len(text) == 0:  # workaround for a bug in VSCode debugger: sys.stdout.write(''); sys.stdout.flush() => crash
            return

        if self.file is not None:
            self.file.write(text)

        self.stdout.write(text)

        if self.should_flush:
            self.flush()

    def flush(self) -> None:
        """Flush written text to both stdout and a file, if open."""
        if self.file is not None:
            self.file.flush()

        self.stdout.flush()

    def close(self) -> None:
        """Flush, close possible files, and remove stdout/stderr mirroring."""
        self.flush()

        # if using multiple loggers, prevent closing in wrong order
        if sys.stdout is self:
            sys.stdout = self.stdout
        if sys.stderr is self:
            sys.stderr = self.stderr

        if self.file is not None:
            self.file.close()
            self.file = None


def get_logger(
    name: str,
    filename: str | None = None,
    mode: str = 'a',
    format: str = '%(asctime)s | %(name)s | %(filename)s | %(levelname)s | - %(message)s',
    auxiliary_handlers: list | None = None,
) -> logging.Logger:
    """Create logger.

    Args:
    ----
        name (str): name of the logger. identical to logging.getLogger(name) if already called once with the same name.
        filename (str | None): filename to where the logs are saved. Default: None
        mode (str): write mode of the file. Default: 'a'
        format (str, optional): logging format.
            Default: '%(asctime)s | %(name)s | %(filename)s | %(levelname)s | - %(message)s'.
        auxiliary_handlers (list, optional): Other user-defined handlers. Default: None

    Returns:
    -------
        logging.Logger: logger object.

    Examples:
    --------
        >>> logger = get_logger('logger-name')

        >>> # this should behave equivalent to logging.getLogger('logger-name')
        >>> # note that other args will be ignored in this situation.
        >>> get_logger('logger-name') == logger
        True

    """
    logger = logging.getLogger(name)

    if len(logger.handlers) > 0:
        return logger

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(format)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if filename is not None:
        file_handler = logging.FileHandler(filename, mode)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    if auxiliary_handlers:
        for handler in auxiliary_handlers:
            logger.addHandler(handler)

    return logger
