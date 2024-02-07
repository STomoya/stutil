"""Path."""
from __future__ import annotations

import datetime
import glob
import os
import shutil
from typing import Any, Callable

import stutil


class Path(str):
    """pathlib.Path like class but is a string object and with additional methods."""

    @property
    def stem(self) -> str:
        """File stem."""
        return os.path.splitext(self.name)[0]

    @property
    def suffix(self) -> str:
        """File suffix."""
        return os.path.splitext(self.name)[-1]

    @property
    def name(self) -> str:
        """File name.

        Returns a black string if the path is a dir.
        """
        return os.path.basename(self) if self.isfile() else ''

    # "/" operator joins paths like pathlib.Path
    def __div__(self, other: str) -> 'Path':
        """Append path-like str to self."""
        if not isinstance(other, str):
            raise TypeError(
                f'unsupported operand type(s) for /: "{self.__class__.__name__}" and "{other.__class__.__name__}"'
            )
        return type(self)(os.path.join(self, other))

    # also enable when true div
    __truediv__ = __div__

    def mkdir(self) -> None:
        """Make directory if self not exists."""
        if not os.path.exists(self):
            os.makedirs(self)

    def expanduser(self) -> 'Path':
        """Expand user."""
        return type(self)(os.path.expanduser(self))

    def glob(
        self,
        recursive: bool = False,
        filter_fn: Callable | None = None,
        sort: bool = False,
        sortkey: Callable | None = None,
    ) -> list:
        """Call glob.glob on self, and optionally sort the result.

        Args:
        ----
            recursive (bool, optional): If True, recursively glob inside subfolders. Default: False.
            filter_fn (Callable | None, optional): Func to filter the glob-ed result. Default: None.
            sort (bool, optional): If True, sort the result. Default: False.
            sortkey (Callable | None, optional): Func for key argument of sorted(). Default: None.

        Returns:
        -------
            list[Path]: list of glob-ed paths.

        """
        glob_pattern = self / ('**/*' if recursive else '*')
        paths = glob.glob(glob_pattern, recursive=recursive)
        if isinstance(filter_fn, Callable):
            paths = [path for path in paths if filter_fn(path)]
        if sort:
            paths = sorted(paths, key=sortkey)
        paths = [type(self)(path) for path in paths]
        return paths

    def exists(self) -> bool:
        """Exists."""
        return os.path.exists(self)

    def isdir(self) -> bool:
        """isdir."""
        return os.path.isdir(self)

    def isfile(self) -> bool:
        """isfile."""
        return os.path.isfile(self)

    def resolve(self) -> 'Path':
        """Resolve path."""
        return type(self)(os.path.realpath(os.path.abspath(self)))

    def dirname(self) -> 'Path':
        """dirname."""
        return type(self)(os.path.dirname(self))

    # functions from shutil
    # Path('./somewhere').rmtree() == shutile.rmtree('./somewhere')
    copy = shutil.copy
    move = shutil.move
    rmtree = shutil.rmtree


class Folder(object):
    """Class for easily handling paths inside a root directory.

    Args:
    ----
        root (str): root directory.
        identify (bool, optional): make root folder identifiable. Default: False.
        identifier (str, optional): identifier. Default: None.

    Examples::
        >>> folder = Folder('./checkpoint')
        >>> print(folder.root) # > './checkpoint'

        >>> # add subfolders
        >>> folder.add_children(image='subfolder1', model='subfolder2/subsubfolder')
        >>> # subfolders can be accessed by name like attrs
        >>> print(folder.image) # > './checkpoint/subfolder1'
        >>> print(folder.model) # > './checkpoint/subfolder2/subsubfolder'

        >>> # "/" operator can be used to join file/folder to root/sub folder
        >>> print(folder.image / 'image.jpg') # > './checkpoint/subfolder1/image.jpg'

        >>> # make all folders and subfolders if not exists.
        >>> folder.mkdir()

        >>> # list all directories as dict
        >>> folder.list()

    """

    def __init__(self, root: str, identify: bool = False, identifier: str | None = None) -> None:
        """Folder."""
        if identify:
            identifier = identifier if identifier is not None else datetime.datetime.now().strftime('%Y.%m.%d.%H.%M.%S')
            root += '_' + identifier

        self._roots = stutil.EasyDict()
        self._roots.root = Path(root)

    def __getattr__(self, __name: str) -> Any:
        """Access by key."""
        try:
            if __name in self._roots:
                return self._roots[__name]
            return self.__dict__[__name]
        except KeyError:
            raise AttributeError(__name)  # noqa: B904,TRY200

    def add_children(self, **kwargs) -> None:
        """Add subfolders to root directory."""
        for name, folder in kwargs.items():
            self._roots[name] = self._roots.root / folder

    def mkdir(self) -> None:
        """Make folders and subfolders if not exists."""
        for name in self._roots:
            self._roots[name].mkdir()

    def list(self) -> dict:
        """List all folders as dict.

        Returns
        -------
            dict: Listed folders.

        """
        return self._roots
