"""Below is taken from: https://github.com/NVlabs/stylegan3/blob/583f2bdd139e014716fc279f23d362959bcc0f39/dnnlib/util.py#L233-L303.

Creates an object using it's name and parameters.
Modified by: STomoya (https://github.com/STomoya)
"""
from __future__ import annotations

import importlib
import sys
import types
from typing import Any, Tuple

__all__ = ['get_obj_by_name', 'call_func_by_name', 'construct_class_by_name']


def _get_module_from_obj_name(obj_name: str) -> Tuple[types.ModuleType, str]:
    """Search for the underlying module behind the name to some python object.

    Returns the module and the object name (original name with module part removed).
    """
    # list alternatives for (module_name, local_obj_name)
    parts = obj_name.split('.')
    name_pairs = [('.'.join(parts[:i]), '.'.join(parts[i:])) for i in range(len(parts), 0, -1)]

    # try each alternative in turn
    for module_name, local_obj_name in name_pairs:
        try:
            module = importlib.import_module(module_name)  # may raise ImportError
            _get_obj_from_module(module, local_obj_name)  # may raise AttributeError
            return module, local_obj_name  # noqa: TRY300
        except Exception:
            pass

    # maybe some of the modules themselves contain errors?
    for module_name, _local_obj_name in name_pairs:
        try:
            importlib.import_module(module_name)  # may raise ImportError
        except ImportError:
            if not str(sys.exc_info()[1]).startswith("No module named '" + module_name + "'"):
                raise

    # maybe the requested attribute is missing?
    for module_name, local_obj_name in name_pairs:
        try:
            module = importlib.import_module(module_name)  # may raise ImportError
            _get_obj_from_module(module, local_obj_name)  # may raise AttributeError
        except ImportError:
            pass

    # we are out of luck, but we have no idea why
    raise ImportError(obj_name)


def _get_obj_from_module(module: types.ModuleType, obj_name: str) -> Any:
    """Traverses the object name and returns the last (rightmost) python object."""
    if obj_name == '':
        return module
    obj = module
    for part in obj_name.split('.'):
        obj = getattr(obj, part)
    return obj


def get_obj_by_name(name: str) -> Any:
    """Find the python object with the given name."""
    module, obj_name = _get_module_from_obj_name(name)
    return _get_obj_from_module(module, obj_name)


def call_func_by_name(*args, func_name: str | None = None, **kwargs) -> Any:
    """Find the python object with the given name and calls it as a function."""
    assert func_name is not None
    func_obj = get_obj_by_name(func_name)
    assert callable(func_obj)
    return func_obj(*args, **kwargs)


def construct_class_by_name(*args: Any, class_name: str | None = None, **kwargs: Any) -> Any:
    """Find the python class with the given name and constructs it with the given arguments.

    Args:
    ----
        *args: Any
            Positional arguments of the class
        class_name: str
            The name of the class. It should be the full name (like torch.optim.Adam).
        **kwargs: Any
            Keyword arguments of the class

    """
    return call_func_by_name(*args, func_name=class_name, **kwargs)
