
import logging


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
