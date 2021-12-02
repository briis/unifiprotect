from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any


def get_nested_attr(obj: Any, attr: str) -> Any:
    attrs = attr.split(".")

    value = obj
    for attr in attrs:
        if not hasattr(value, attr):
            return None
        value = getattr(value, attr)

    if isinstance(value, Enum):
        value = value.value

    return value


def get_datetime_attr(dt: datetime | None) -> str | None:
    return None if dt is None else dt
