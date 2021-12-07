"""The unifiprotect integration models."""
from __future__ import annotations

from dataclasses import dataclass

from pyunifiprotect import ProtectApiClient

from .data import ProtectData


@dataclass
class ProtectEntryData:
    """Data for the unifiprotect integration."""

    protect_data: ProtectData
    protect: ProtectApiClient
    disable_stream: bool
