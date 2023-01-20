
import datetime


def timezone(offset: int, name: str=None) -> datetime.tzinfo:
    """wrapper for datetime.timezone, supporting int for offset.

    Args:
        offset (int): offset.
        name (str, optional): name. Defaults to None.

    Returns:
        datetime.tzinfo: tzinfo
    """
    return datetime.timezone(datetime.timedelta(hours=offset), name=name)


def get_jst_timezone() -> datetime.tzinfo:
    """create and return a JST (UCT+9) tzinfo object.

    Returns:
        tzinfo: JST tzinfo
    """
    return timezone(9, 'JST')
