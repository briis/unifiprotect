"""This component provides number entities for UniFi Protect."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from pyunifiprotect.data.devices import Camera, Light

from .const import DOMAIN
from .data import ProtectData
from .entity import ProtectDeviceEntity, async_all_device_entities
from .models import ProtectSetableKeysMixin


@dataclass
class NumberKeysMixin:
    """Mixin for required keys."""

    ufp_max: int
    ufp_min: int
    ufp_step: int


@dataclass
class ProtectNumberEntityDescription(
    ProtectSetableKeysMixin, NumberEntityDescription, NumberKeysMixin
):
    """Describes UniFi Protect Number entity."""


def _get_pir_duration(obj: Any) -> int:
    assert isinstance(obj, Light)
    return int(obj.light_device_settings.pir_duration.total_seconds())


async def _set_pir_duration(obj: Any, value: float) -> None:
    assert isinstance(obj, Light)
    await obj.set_duration(timedelta(seconds=value))


CAMERA_NUMBERS: tuple[ProtectNumberEntityDescription, ...] = (
    ProtectNumberEntityDescription(
        key="wdr_value",
        name="Wide Dynamic Range",
        icon="mdi:state-machine",
        entity_category=EntityCategory.CONFIG,
        ufp_min=0,
        ufp_max=3,
        ufp_step=1,
        ufp_required_field="feature_flags.has_wdr",
        ufp_value="isp_settings.wdr",
        ufp_set_method="set_wdr_level",
    ),
    ProtectNumberEntityDescription(
        key="mic_level",
        name="Microphone Level",
        icon="mdi:microphone",
        entity_category=EntityCategory.CONFIG,
        ufp_min=0,
        ufp_max=100,
        ufp_step=1,
        ufp_required_field="feature_flags.has_mic",
        ufp_value="mic_volume",
        ufp_set_method="set_mic_volume",
    ),
    ProtectNumberEntityDescription(
        key="zoom_position",
        name="Zoom Level",
        icon="mdi:magnify-plus-outline",
        entity_category=EntityCategory.CONFIG,
        ufp_min=0,
        ufp_max=100,
        ufp_step=1,
        ufp_required_field="feature_flags.can_optical_zoom",
        ufp_value="isp_settings.zoom_position",
        ufp_set_method="set_camera_zoom",
    ),
    ProtectNumberEntityDescription(
        key="duration",
        name="Chime Duration",
        icon="mdi:camera-timer",
        entity_category=EntityCategory.CONFIG,
        ufp_min=0,
        ufp_max=10000,
        ufp_step=100,
        ufp_required_field="feature_flags.has_chime",
        ufp_value="chime_duration",
        ufp_set_method="set_chime_duration",
    ),
)

LIGHT_NUMBERS: tuple[ProtectNumberEntityDescription, ...] = (
    ProtectNumberEntityDescription(
        key="sensitivity",
        name="Motion Sensitivity",
        icon="mdi:walk",
        entity_category=EntityCategory.CONFIG,
        ufp_min=0,
        ufp_max=100,
        ufp_step=1,
        ufp_required_field=None,
        ufp_value="light_device_settings.pir_sensitivity",
        ufp_set_method="set_sensitivity",
    ),
    ProtectNumberEntityDescription(
        key="duration",
        name="Auto-shutoff Duration",
        icon="mdi:camera-timer",
        entity_category=EntityCategory.CONFIG,
        ufp_min=15,
        ufp_max=900,
        ufp_step=15,
        ufp_required_field=None,
        ufp_value_fn=_get_pir_duration,
        ufp_set_method_fn=_set_pir_duration,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up number entities for UniFi Protect integration."""
    data: ProtectData = hass.data[DOMAIN][entry.entry_id]
    entities: list[ProtectDeviceEntity] = async_all_device_entities(
        data,
        ProtectNumbers,
        camera_descs=CAMERA_NUMBERS,
        light_descs=LIGHT_NUMBERS,
    )

    async_add_entities(entities)


class ProtectNumbers(ProtectDeviceEntity, NumberEntity):
    """A UniFi Protect Number Entity."""

    device: Camera | Light
    entity_description: ProtectNumberEntityDescription

    def __init__(
        self,
        data: ProtectData,
        device: Camera | Light,
        description: ProtectNumberEntityDescription,
    ) -> None:
        """Initialize the Number Entities."""
        super().__init__(data, device, description)
        self._attr_max_value = self.entity_description.ufp_max
        self._attr_min_value = self.entity_description.ufp_min
        self._attr_step = self.entity_description.ufp_step

    @callback
    def _async_update_device_from_protect(self) -> None:
        super()._async_update_device_from_protect()
        self._attr_value = self.entity_description.get_ufp_value(self.device)

    async def async_set_value(self, value: float) -> None:
        """Set new value."""
        await self.entity_description.ufp_set(self.device, value)
