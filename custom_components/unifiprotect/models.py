"""The unifiprotect integration models."""
from __future__ import annotations

from dataclasses import dataclass

from pyunifiprotect import UpvServer

from .data import UnifiProtectData


@dataclass
class UnifiProtectEntryData:
    """Data for the unifiprotect integration."""

    protect_data: UnifiProtectData
    upv: UpvServer
    disable_stream: bool
    doorbell_text: str | None
