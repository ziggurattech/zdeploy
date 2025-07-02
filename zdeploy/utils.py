"""Utility helpers for zdeploy."""


def reformat_time(time):
    """Return ``time`` in "Nh, Nm, and Ns" format."""

    h, m, s = [int(float(x)) for x in (f"{time}").split(":")]
    return f"{h}h, {m}m, and {s}s"
