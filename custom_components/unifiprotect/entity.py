"""Shared Entity definition for UniFi Protect Integration."""
from __future__ import annotations

import collections
from datetime import timedelta
import hashlib
import logging
from random import SystemRandom
from typing import Any, Final, Sequence

from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.core import callback
import homeassistant.helpers.device_registry as dr
from homeassistant.helpers.dispatcher import (
    async_dispatcher_connect,
    async_dispatcher_send,
)
from homeassistant.helpers.entity import DeviceInfo, Entity, EntityDescription
from pyunifiprotect.data.base import ProtectAdoptableDeviceModel
from pyunifiprotect.data.devices import Camera, Light, Sensor, Viewer
from pyunifiprotect.data.nvr import NVR
from pyunifiprotect.data.types import ModelType, StateType

from .const import DEFAULT_ATTRIBUTION, DEFAULT_BRAND, DOMAIN, EVENT_UPDATE_TOKENS
from .data import ProtectData
from .models import ProtectRequiredKeysMixin
from .utils import get_nested_attr

TOKEN_CHANGE_INTERVAL: Final = timedelta(minutes=1)
_RND: Final = SystemRandom()
_LOGGER = logging.getLogger(__name__)


@callback
def _async_device_entities(
    data: ProtectData,
    klass: type[ProtectDeviceEntity],
    model_type: ModelType,
    descs: Sequence[ProtectRequiredKeysMixin],
) -> list[ProtectDeviceEntity]:
    if len(descs) == 0:
        return []

    entities: list[ProtectDeviceEntity] = []
    for device in data.get_by_types({model_type}):
        assert isinstance(device, (Camera, Light, Sensor, Viewer))
        for description in descs:
            assert isinstance(description, EntityDescription)
            if description.ufp_required_field:
                required_field = get_nested_attr(device, description.ufp_required_field)
                if not required_field:
                    continue

            entities.append(
                klass(
                    data,
                    device=device,
                    description=description,
                )
            )
            _LOGGER.debug(
                "Adding %s entity %s for %s",
                klass.__name__,
                description.name,
                device.name,
            )

    return entities


@callback
def async_all_device_entities(
    data: ProtectData,
    klass: type[ProtectDeviceEntity],
    camera_descs: Sequence[ProtectRequiredKeysMixin] | None = None,
    light_descs: Sequence[ProtectRequiredKeysMixin] | None = None,
    sense_descs: Sequence[ProtectRequiredKeysMixin] | None = None,
    viewer_descs: Sequence[ProtectRequiredKeysMixin] | None = None,
    all_descs: Sequence[ProtectRequiredKeysMixin] | None = None,
) -> list[ProtectDeviceEntity]:
    """Generate a list of all the device entities."""
    all_descs = list(all_descs or [])
    camera_descs = list(camera_descs or []) + all_descs
    light_descs = list(light_descs or []) + all_descs
    sense_descs = list(sense_descs or []) + all_descs
    viewer_descs = list(viewer_descs or []) + all_descs

    return (
        _async_device_entities(data, klass, ModelType.CAMERA, camera_descs)
        + _async_device_entities(data, klass, ModelType.LIGHT, light_descs)
        + _async_device_entities(data, klass, ModelType.SENSOR, sense_descs)
        + _async_device_entities(data, klass, ModelType.VIEWPORT, viewer_descs)
    )


class ProtectDeviceEntity(Entity):
    """Base class for UniFi protect entities."""

    def __init__(
        self,
        data: ProtectData,
        device: ProtectAdoptableDeviceModel | None = None,
        description: EntityDescription | None = None,
    ) -> None:
        """Initialize the entity."""
        super().__init__()
        self._attr_should_poll = False

        self.data: ProtectData = data

        if device and not hasattr(self, "device"):
            self.device: ProtectAdoptableDeviceModel = device

        if description and not hasattr(self, "entity_description"):
            self.entity_description = description
        elif hasattr(self, "entity_description"):
            description = self.entity_description

        if description is None:
            self._attr_unique_id = f"{self.device.id}"
            self._attr_name = f"{self.device.name}"
        else:
            self._attr_unique_id = f"{self.device.id}_{description.key}"
            name = description.name or ""
            self._attr_name = f"{self.device.name} {name.title()}"

        self._async_set_device_info()
        self._async_update_device_from_protect()

    async def async_update(self) -> None:
        """Update the entity.

        Only used by the generic entity update service.
        """
        await self.data.async_refresh()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return UniFi Protect device attributes."""
        attrs = super().extra_state_attributes or {}
        return {
            **attrs,
            ATTR_ATTRIBUTION: DEFAULT_ATTRIBUTION,
            **self._extra_state_attributes,
        }

    @callback
    def _async_set_device_info(self) -> None:
        self._attr_device_info = DeviceInfo(
            name=self.device.name,
            manufacturer=DEFAULT_BRAND,
            model=self.device.type,
            via_device=(DOMAIN, self.data.api.bootstrap.nvr.mac),
            sw_version=self.device.firmware_version,
            connections={(dr.CONNECTION_NETWORK_MAC, self.device.mac)},
            configuration_url=self.device.protect_url,
        )

    @callback
    def _async_update_extra_attrs_from_protect(  # pylint: disable=no-self-use
        self,
    ) -> dict[str, Any]:
        """Calculate extra state attributes. Primarily for subclass to override."""
        return {}

    @callback
    def _async_update_device_from_protect(self) -> None:
        """Update Entity object from Protect device."""
        if self.data.last_update_success:
            assert self.device.model
            devices = getattr(self.data.api.bootstrap, f"{self.device.model.value}s")
            self.device = devices[self.device.id]

        self._attr_available = (
            self.data.last_update_success and self.device.state == StateType.CONNECTED
        )
        self._extra_state_attributes = self._async_update_extra_attrs_from_protect()

    @callback
    def _async_updated_event(self) -> None:
        """Call back for incoming data."""
        self._async_update_device_from_protect()
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        self.async_on_remove(
            self.data.async_subscribe_device_id(
                self.device.id, self._async_updated_event
            )
        )


class ProtectNVREntity(ProtectDeviceEntity):
    """Base class for unifi protect entities."""

    def __init__(
        self,
        entry: ProtectData,
        device: NVR,
        description: EntityDescription | None = None,
    ) -> None:
        """Initialize the entity."""
        # ProtectNVREntity is intentionally a separate base class
        self.device: NVR = device  # type: ignore
        super().__init__(entry, description=description)

    @callback
    def _async_set_device_info(self) -> None:
        self._attr_device_info = DeviceInfo(
            connections={(dr.CONNECTION_NETWORK_MAC, self.device.mac)},
            identifiers={(DOMAIN, self.device.mac)},
            manufacturer=DEFAULT_BRAND,
            name=self.device.name,
            model=self.device.type,
            sw_version=str(self.device.version),
            configuration_url=self.device.api.base_url,
        )

    @callback
    def _async_update_device_from_protect(self) -> None:
        if self.data.last_update_success:
            self.device = self.data.api.bootstrap.nvr

        self._attr_available = self.data.last_update_success
        self._extra_state_attributes = self._async_update_extra_attrs_from_protect()


class AccessTokenMixin(Entity):
    """Adds access_token attribute and provides access tokens for use for anonymous views."""

    @property
    def access_tokens(self) -> collections.deque[str]:
        """Get valid access_tokens for current entity."""
        assert isinstance(self, ProtectDeviceEntity)
        return self.data.async_get_or_create_access_tokens(self.entity_id)

    @callback
    def _async_update_and_write_token(self) -> None:
        _LOGGER.debug("Updating access tokens for %s", self.entity_id)
        self.async_update_token()
        self.async_write_ha_state()

    @callback
    def async_update_token(self) -> None:
        """Update the used token."""
        self.access_tokens.append(
            hashlib.sha256(_RND.getrandbits(256).to_bytes(32, "little")).hexdigest()
        )

    @callback
    def _trigger_update_tokens(self, *args: Any, **kwargs: Any) -> None:
        assert isinstance(self, ProtectDeviceEntity)
        async_dispatcher_send(
            self.hass,
            f"{EVENT_UPDATE_TOKENS}-{self.entity_description.key}-{self.entity_id}",
        )

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass.

        Injects callbacks to update access tokens automatically
        """
        await super().async_added_to_hass()

        self.async_update_token()
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                f"{EVENT_UPDATE_TOKENS}-{self.entity_id}",
                self._async_update_and_write_token,
            )
        )
        self.async_on_remove(
            self.hass.helpers.event.async_track_time_interval(
                self._trigger_update_tokens, TOKEN_CHANGE_INTERVAL
            )
        )
