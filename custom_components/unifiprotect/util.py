"""Utility class for UniFi Protect."""

import datetime as dt

from homeassistant.util import dt as hassdt


def dt_local(dattim: str) -> str:
    """Ensures datetime is in local time."""

    input_dt = dt.datetime.strptime(dattim, "%Y-%m-%d %H:%M:%S")
    local_dt = hassdt.as_local(input_dt)
    return local_dt.strftime("%Y-%m-%d %H:%M:%S")
