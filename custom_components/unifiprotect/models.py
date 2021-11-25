"""The unifiprotect integration models."""
from __future__ import annotations

from dataclasses import dataclass

from pyunifiprotect import ProtectApiClient

from .data import UnifiProtectData


@dataclass
class UnifiProtectEntryData:
    """Data for the unifiprotect integration."""

    protect_data: UnifiProtectData
    protect: ProtectApiClient
    disable_stream: bool
    doorbell_text: str | None
