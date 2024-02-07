"""easy dict."""

# ruff: noqa: D105,D107

from typing import Any


class EasyDict(dict):
    """dict that can access keys like attributes."""

    def __init__(self, *args, **kwargs):
        if len(args) > 1:
            raise TypeError(f'EasyDict expected at most 1 arguments, got {len(args)}')

        if len(args) == 0:
            init_dict = {}
        elif len(args) > 0:
            init_dict = args[0]

        if kwargs != {}:
            init_dict.update(kwargs)

        for key, value in init_dict.items():
            self.__setattr__(key, value)

    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)  # noqa: B904,TRY200

    def __setattr__(self, name: str, value: Any) -> None:
        if isinstance(value, dict) and not isinstance(value, type(self)):
            self[name] = type(self)(value)
        else:
            self[name] = value

    def __delattr__(self, name: str) -> None:
        del self[name]
