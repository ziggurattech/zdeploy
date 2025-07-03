"""Utility helpers for zdeploy."""


from datetime import timedelta
from typing import Union
import logging


def str2bool(value: str) -> bool:
    """Return ``True`` if ``value`` is a truthy string."""

    value = value.lower()
    if value in {"yes", "y", "true", "t", "e", "enable"}:
        return True

    logging.warning("'%s' is not recognized as a true value, defaulting to False", value)
    return False


def reformat_time(time: Union[str, timedelta]) -> str:
    """Return ``time`` in "Nh, Nm, and Ns" format."""

    if isinstance(time, timedelta):
        time = str(time)
    h, m, s = [int(float(x)) for x in time.split(":")]
    return f"{h}h, {m}m, and {s}s"
