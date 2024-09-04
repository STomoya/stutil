"""exceptions."""

from __future__ import annotations

import warnings
from functools import wraps
from typing import Callable

__all__ = ['warn_deprecated', 'deprecated', 'STException']


class STException(Exception):
    """Base class for all STomoya related exceptions."""


def warn_deprecated(name: str, favor_of: str | None = None, recommendation: str | None = None) -> None:
    """Call warnings.warn for deprecations.

    Args:
        name (str): name of the deprecated code.
        favor_of (str, optional): reason of deprecation. Default: None.
        recommendation (str, optional): recommendation to use other function. Defaults to None.

    """
    deprecation_text = f'"{name}" is deprecated'
    if favor_of is not None:
        deprecation_text += f' in favor of "{favor_of}"'
    deprecation_text += '.'
    if recommendation is not None:
        deprecation_text += f' Please use "{recommendation}".'

    warnings.warn(deprecation_text, FutureWarning, stacklevel=1)


def deprecated(favor_of: str | None = None, recommendation: str | None = None) -> Callable:
    """Wrap deprecated function.

    Decorator to call deprecation warnings when the wrapped callable is called.

    Args:
        favor_of (str, optional): reason of deprecation. Default: None.
        recommendation (str, optional): recommendation to use other function. Defaults to None.

    Returns:
        Callable: wrapped callable

    Examples:
        ```
        @deprecated(favor_of='func_v2', recommendation='func_v2')
        def func_v1(): pass

        # it can also decorate a class
        @deprecated(favor_of='Cls_v2', recommendation='Cls_v2')
        class Cls_V1: pass
        ```

    """

    def decorator(wrapped):
        @wraps(wrapped)
        def inner(*args, **kwargs):
            warn_deprecated(wrapped.__qualname__, favor_of, recommendation)
            return wrapped(*args, **kwargs)

        return inner

    return decorator
