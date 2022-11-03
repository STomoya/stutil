
import logging
import sys
from contextlib import contextmanager
from typing import Union


__all__=[
    'open_redirect_std_stream',
    'close_redirect_std_stream',
    'redirect_stds',
    'get_logger'
]


_stream = None

def open_redirect_std_stream(filename: str=None, mode: str='a'):
    global _stream
    if _stream is None:
        _stream = RedirectStdStream(filename, mode)
    return _stream


def close_redirect_std_stream():
    global _stream
    if _stream is not None:
        _stream.close()
    _stream = None


@contextmanager
def redirect_stds(filename: str=None, mode: str='a'):
    open_redirect_std_stream(filename, mode)
    yield
    close_redirect_std_stream()


class RedirectStdStream(object):
    '''Redirect stderr to stdout, optionally print stdout to a file, and optionally force flushing on both stdout and the file.
    from: https://github.com/NVlabs/stylegan3/blob/583f2bdd139e014716fc279f23d362959bcc0f39/dnnlib/util.py#L56-L112
    '''

    def __init__(self, file_name: str = None, file_mode: str = "a", should_flush: bool = True):
        self.file = None

        if file_name is not None:
            self.file = open(file_name, file_mode)

        self.should_flush = should_flush
        self.stdout = sys.stdout
        self.stderr = sys.stderr

        sys.stdout = self
        sys.stderr = self

    def write(self, text: Union[str, bytes]) -> None:
        """Write text to stdout (and a file) and optionally flush.
        Args:
            text (Union[str, bytes]): Text to write.
        """
        if isinstance(text, bytes):
            text = text.decode()
        if len(text) == 0: # workaround for a bug in VSCode debugger: sys.stdout.write(''); sys.stdout.flush() => crash
            return

        if self.file is not None:
            self.file.write(text)

        self.stdout.write(text)

        if self.should_flush:
            self.flush()

    def flush(self) -> None:
        """Flush written text to both stdout and a file, if open.
        """
        if self.file is not None:
            self.file.flush()

        self.stdout.flush()

    def close(self) -> None:
        """Flush, close possible files, and remove stdout/stderr mirroring.
        """
        self.flush()

        # if using multiple loggers, prevent closing in wrong order
        if sys.stdout is self:
            sys.stdout = self.stdout
        if sys.stderr is self:
            sys.stderr = self.stderr

        if self.file is not None:
            self.file.close()
            self.file = None


def get_logger(name: str,
    filename: str=None, mode: str='a',
    format: str='%(asctime)s | %(name)s | %(filename)s | %(levelname)s | - %(message)s',
    auxiliary_handlers: list=None
) -> logging.Logger:
    """setup and return logger

    Args:
        name (str): name of the logger. identical to logging.getLogger(name) if already called once with the same name.
        format (str, optional): logging format. Default: '%(asctime)s | %(name)s | %(filename)s | %(levelname)s | - %(message)s'.
        auxiliary_handlers (list, optional): Other user-defined handlers. Default: None

    Returns:
        logging.Logger: logger object.

    Examples:
        >>> logger = get_logger('logger-name')
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
