"""Utility helpers for zdeploy."""


from datetime import timedelta
from typing import Union


def str2bool(value: str) -> bool:
    """Return ``True`` for 'yes' or 'y' and ``False`` for 'no' or 'n'."""

    value = value.lower()
    if value in ("yes", "y"):
        return True
    if value in ("no", "n"):
        return False
    raise ValueError(f"Invalid value: {value}")


def reformat_time(time: Union[str, timedelta]) -> str:
    """Return ``time`` in "Nh, Nm, and Ns" format."""

    if isinstance(time, timedelta):
        time = str(time)
    h, m, s = [int(float(x)) for x in time.split(":")]
    return f"{h}h, {m}m, and {s}s"
