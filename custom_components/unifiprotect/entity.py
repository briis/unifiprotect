"""Shared Entity definition for Unifi Protect Integration."""
from __future__ import annotations

import collections
from datetime import timedelta
import hashlib
from random import SystemRandom
from typing import Any, Final

from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.core import callback
import homeassistant.helpers.device_registry as dr
from homeassistant.helpers.entity import DeviceInfo, Entity, EntityDescription
from pyunifiprotect import ProtectApiClient
from pyunifiprotect.data.base import ProtectAdoptableDeviceModel, ProtectDeviceModel
from pyunifiprotect.data.nvr import NVR
from pyunifiprotect.data.types import ModelType

from .const import ATTR_DEVICE_MODEL, DEFAULT_ATTRIBUTION, DEFAULT_BRAND, DOMAIN
from .data import UnifiProtectData

TOKEN_CHANGE_INTERVAL: Final = timedelta(minutes=5)
_RND: Final = SystemRandom()


class UnifiProtectEntity(Entity):
    """Base class for unifi protect entities."""

    def __init__(
        self,
        protect: ProtectApiClient,
        protect_data: UnifiProtectData,
        device: ProtectDeviceModel,
        description: EntityDescription | None,
    ) -> None:
        """Initialize the entity."""
        super().__init__()
        self._attr_should_poll = False

        if description and not hasattr(self, "entity_description"):
            self.entity_description = description
        if not hasattr(self, "device"):
            self.device: ProtectDeviceModel = device
        self.protect: ProtectApiClient = protect
        self.protect_data: UnifiProtectData = protect_data
        if description is None:
            self._attr_unique_id = f"{self.device.id}"
        else:
            self._attr_unique_id = f"{self.device.id}_{description.key}"

        if isinstance(self.device, NVR):
            self._attr_device_info = DeviceInfo(
                connections={(dr.CONNECTION_NETWORK_MAC, self.device.mac)},
                identifiers={(DOMAIN, self.device.mac)},
                manufacturer=DEFAULT_BRAND,
                name=self.device.name,
                model=self.device.type,
                sw_version=str(self.device.version),
                configuration_url=self.device.api.base_url,
            )
        else:
            assert isinstance(self.device, ProtectAdoptableDeviceModel)
            self._attr_device_info = DeviceInfo(
                name=self.device.name,
                manufacturer=DEFAULT_BRAND,
                model=self.device.type,
                via_device=(DOMAIN, self.protect.bootstrap.nvr.mac),
                sw_version=self.device.firmware_version,
                connections={(dr.CONNECTION_NETWORK_MAC, self.device.mac)},
                configuration_url=self.device.protect_url,
            )

    async def async_update(self) -> None:
        """Update the entity.

        Only used by the generic entity update service.
        """
        await self.protect_data.async_refresh()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return common attributes"""
        return {
            ATTR_ATTRIBUTION: DEFAULT_ATTRIBUTION,
            ATTR_DEVICE_MODEL: self.device.type,
        }

    @callback
    def _async_update_device_from_protect(self) -> None:
        if self.protect_data.last_update_success:
            if self.device.model == ModelType.NVR:
                self.device = self.protect.bootstrap.nvr
            else:
                assert self.device.model
                devices = getattr(self.protect.bootstrap, f"{self.device.model.value}s")
                self.device = devices[self.device.id]

        self._attr_available = self.protect_data.last_update_success
        if isinstance(self.device, ProtectAdoptableDeviceModel):
            self._attr_available = self._attr_available and self.device.is_connected

    @callback
    def _async_updated_event(self) -> None:
        self._async_update_device_from_protect()
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        self.async_on_remove(
            self.protect_data.async_subscribe_device_id(
                self.device.id, self._async_updated_event
            )
        )


class AccessTokenMixin(Entity):
    def __init__(self, *args, **kwargs) -> None:
        self.access_tokens: collections.deque = collections.deque([], 2)
        self.async_update_token()

    @callback
    def async_update_token(self) -> None:
        """Update the used token."""
        self.access_tokens.append(
            hashlib.sha256(_RND.getrandbits(256).to_bytes(32, "little")).hexdigest()
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the extra state attributes."""
        attrs = super().extra_state_attributes or {}
        return {
            **attrs,
            "access_token": self.access_tokens[-1],
        }
