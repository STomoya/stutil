"""Pure python utilities."""

from __future__ import annotations

import datetime
import functools
import glob
import importlib
import json
import os
import re
import sys
import traceback
from argparse import Namespace
from collections.abc import Iterable
from typing import Any, Callable

from stutil.timezone import get_jst_timezone

__all__ = [
    'check_folder',
    'dynamic_default',
    'get_now_string',
    'glob_inside',
    'natural_sort',
    'prod',
    'recursive_apply',
    'save_command_args',
    'save_exec_status',
    'import_all_modules',
]


def dynamic_default(value: Any | None, default_value: Any) -> Any:
    """Dynamic default value.

    Args:
        value (Any | None): A value or None.
        default_value (Any): The default value used when value is None.

    Returns:
        Any: The selected value depending on the arguments.

    """
    return value if value is not None else default_value


def prod(iter: Iterable) -> int | float:
    """numpy.prod for python iterables.

    Use math.prod() for python >= 3.8.

    Args:
        iter (Iterable): An iterable containing numeric values

    Returns:
        int|float: The calculated product of all elements in the given iterable.

    """
    result = 1
    for value in iter:
        result *= value
    return result


def save_command_args(args: Namespace, filename: str = 'args.json') -> None:
    """Save Namespace object to json file.

    Args:
        args (Namespace): Parsed command line arguments as an argparse.Namespace object.
        filename (str, optional): Name of the file to save the arguments. Default: 'args.json'

    """
    args_dict = vars(args)
    with open(filename, 'w') as fout:
        json.dump(args_dict, fout, indent=2)


def check_folder(folder: str, make: bool = False) -> bool:
    """Check if a folder exists and create it if not.

    Args:
        folder (str): The folder to check the existance.
        make (bool, optional): If True, create the folder of not exists. Default: False.

    Returns:
        bool: A boolean indicating the existance of the folder.

    """
    exists = os.path.exists(folder)
    if make and not exists:
        os.makedirs(folder)
    return exists


def glob_inside(folder: str, pattern: str = '*', recursive: bool = True) -> list[str]:
    """Glob for files/dirs that matches pattern.

    Args:
        folder (str): Root folder to glob inside.
        pattern (str, optional): Glob pattern. Default: '*'.
        recursive (bool, optional): Whether to recursively glob into child folders. Default: True.

    Returns:
        list[str]: Lst of glob-ed paths.

    """
    pattern = f'**/{pattern}' if recursive else pattern
    return glob.glob(os.path.join(folder, pattern), recursive=recursive)


# from: https://github.com/google/flax/blob/2387439a6f5c88627754905e6feadac4f33d9800/flax/training/checkpoints.py
UNSIGNED_FLOAT_RE = re.compile(r'[-+]?((?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)')


def natural_sort(iter: list[str], reverse: bool = False) -> list[str]:
    """Sort files by numbers.

    Args:
        iter (list[str]): An iterable to sort.
        reverse (bool, optional): Reverse sorting. Default: False

    Returns:
        list[str]: The sorted iterable.

    """

    def maybe_num(s):
        return float(s) if UNSIGNED_FLOAT_RE.match(s) else s

    def split_keys(s):
        return [maybe_num(c) for c in UNSIGNED_FLOAT_RE.split(s)]

    return sorted(iter, key=split_keys, reverse=reverse)


def recursive_apply(func: Callable, data: Any, cond_fn: Callable) -> Any:
    """Recursively apply func to data that satisfies cond_fn.

    Args:
        func (Callable): The function to apply
        data (Any): Data to be applied
        cond_fn (Callable): A function that returns a bool, which decides whether to apply the func or not.

    Returns:
        Any: data, with func applied.

    """
    if isinstance(data, (tuple, list)):
        return type(data)(recursive_apply(func, element, cond_fn) for element in data)
    elif isinstance(data, dict):
        return {key: recursive_apply(func, value, cond_fn) for key, value in data.items()}
    elif cond_fn(data):
        data = func(data)
    return data


def get_now_string(format: str = '%Y%m%d%H%M%S', use_jst: bool = True) -> str:
    """Get datetime.datetime.now() as string.

    Args:
        format (str, optional): format of the datetime. Default: '%Y%m%d%H%M%S'.
        use_jst (bool, optional): use jst timezone. Default: True.

    Returns:
        str: datetime.

    """
    return datetime.datetime.now(tz=get_jst_timezone() if use_jst else None).strftime(format)


def save_exec_status(path: str = './execstatus.txt', mode: str = 'a', use_jst: bool = True) -> Callable:
    """Save execution status to a file.

    Useful if you cannot access traceback messages like inside detached docker containers.

    Args:
        path (str, optional): File to save the output to.. Default: './execstatus.txt'.
        mode (str, optional): File open mode. 'w' will overwrite previous outputs. Default: 'a'.
        use_jst (bool, optional): Use Japan Standard Time (JST). if False use UCT. Default: True

    Raises:
        Exception: Any exeception raised inside the function.

    Returns:
        Callable: A decorator which wraps a function to save the execution status.

    Examples:
        ```
        @storch.save_exec_status('./path/to/output.txt', 'a')
        def hello():
            print('hello')
        # OR
        def hello():
            print('hello')
        hello = storch.save_exec_status('./path/to/output.txt', 'a')(hello)
        ```

    """
    messgae_format = (
        ''
        + '**  MAIN CALL   **: {func_name}\n'
        + '**  STATUS      **: {status}\n'
        + '**  START TIME  **: {start_time}\n'
        + '**  END TIME    **: {end_time}\n'
        + '**  DURATION    **: {duration}\n'
    )

    date_format = '%Y-%m-%d %H:%M:%S'

    def _save(message):
        with open(path, mode) as fp:
            fp.write(message)

    def decorator(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            start_time = get_now_string(date_format, use_jst)
            func_name = func.__qualname__

            try:
                retval = func(*args, **kwargs)

                # successful run
                end_time = get_now_string(date_format, use_jst)
                duration = end_time - start_time
                message = messgae_format.format(
                    func_name=func_name,
                    status='FINISHED 🐈',
                    start_time=start_time.strftime(date_format),
                    end_time=end_time.strftime(date_format),
                    duration=str(duration),
                )
                _save(message)

                return retval  # noqa: TRY300

            except Exception as ex:
                # error
                end_time = get_now_string(date_format, use_jst)
                duration = end_time - start_time
                tb = traceback.format_exc()
                message = (
                    messgae_format.format(
                        func_name=func_name,
                        status='CRASHED 👿',
                        start_time=start_time.strftime(date_format),
                        end_time=end_time.strftime(date_format),
                        duration=str(duration),
                    )
                    + f'**  ERROR       **: {ex}\n'
                    + f'**  TRACEBACK   **: \n{tb}\n'
                )  # add traceback and error message
                _save(message)

                raise

        return inner

    return decorator


def import_all_modules(root: str, base_module: str) -> None:
    """Import all modules under root.

    from: https://github.com/facebookresearch/ClassyVision/blob/309d4f12431c6b4d8540010a781dc2aa25fe88e7/classy_vision/generic/registry_utils.py#L14-L20

    Args:
        root (str): Absolute path to the directory of the module to import.
        base_module (str): Name of the base module.

    """
    for file in os.listdir(root):
        if file.endswith(('.py', '.pyc')) and not file.startswith('_'):
            module = file[: file.find('.py')]
            if module not in sys.modules:
                module_name = '.'.join([base_module, module])
                importlib.import_module(module_name)
