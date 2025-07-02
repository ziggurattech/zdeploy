"""Utility helpers for zdeploy."""


from datetime import timedelta
from typing import Union


def reformat_time(time: Union[str, timedelta]) -> str:
    """Return ``time`` in "Nh, Nm, and Ns" format."""

    if isinstance(time, timedelta):
        time = str(time)
    h, m, s = [int(float(x)) for x in time.split(":")]
    return f"{h}h, {m}m, and {s}s"
