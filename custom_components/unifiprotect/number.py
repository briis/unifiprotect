"""This component provides number entities for Unifi Protect."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import logging

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from pyunifiprotect.data import ModelType

from .const import DEVICES_WITH_CAMERA, DOMAIN, ENTITY_CATEGORY_CONFIG
from .entity import UnifiProtectEntity
from .models import UnifiProtectEntryData
from .utils import get_nested_attr

_LOGGER = logging.getLogger(__name__)

_KEY_WDR = "wdr_value"
_KEY_MIC_LEVEL = "mic_level"
_KEY_ZOOM_POS = "zoom_position"
_KEY_SENSITIVITY = "semsitivity"
_KEY_DURATION = "duration"
_KEY_CHIME = "chime_duration"


@dataclass
class UnifiprotectRequiredKeysMixin:
    """Mixin for required keys."""

    ufp_max: int
    ufp_min: int
    ufp_step: int
    ufp_device_types: set[ModelType]
    ufp_required_field: str | None
    ufp_value: str
    ufp_set_function: str


@dataclass
class UnifiProtectNumberEntityDescription(
    NumberEntityDescription, UnifiprotectRequiredKeysMixin
):
    """Describes Unifi Protect Number entity."""


NUMBER_TYPES: tuple[UnifiProtectNumberEntityDescription, ...] = (
    UnifiProtectNumberEntityDescription(
        key=_KEY_WDR,
        name="Wide Dynamic Range",
        icon="mdi:state-machine",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_min=0,
        ufp_max=3,
        ufp_step=1,
        ufp_device_types=DEVICES_WITH_CAMERA,
        ufp_required_field="feature_flags.has_wdr",
        ufp_value="isp_settings.wdr",
        ufp_set_function="set_wdr_level",
    ),
    UnifiProtectNumberEntityDescription(
        key=_KEY_MIC_LEVEL,
        name="Microphone Level",
        icon="mdi:microphone",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_min=0,
        ufp_max=100,
        ufp_step=1,
        ufp_device_types=DEVICES_WITH_CAMERA,
        ufp_required_field="feature_flags.has_mic",
        ufp_value="mic_volume",
        ufp_set_function="set_mic_volume",
    ),
    UnifiProtectNumberEntityDescription(
        key=_KEY_ZOOM_POS,
        name="Zoom Position",
        icon="mdi:magnify-plus-outline",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_min=0,
        ufp_max=100,
        ufp_step=1,
        ufp_device_types=DEVICES_WITH_CAMERA,
        ufp_required_field="feature_flags.can_optical_zoom",
        ufp_value="isp_settings.zoom_position",
        ufp_set_function="set_camera_zoom",
    ),
    UnifiProtectNumberEntityDescription(
        key=_KEY_SENSITIVITY,
        name="Motion Sensitivity",
        icon="mdi:walk",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_min=0,
        ufp_max=100,
        ufp_step=1,
        ufp_device_types={ModelType.LIGHT},
        ufp_required_field=None,
        ufp_value="light_device_settings.pir_sensitivity",
        ufp_set_function="set_sensitivity",
    ),
    UnifiProtectNumberEntityDescription(
        key=_KEY_DURATION,
        name="Duration",
        icon="mdi:camera-timer",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_min=15,
        ufp_max=900,
        ufp_step=15,
        ufp_device_types={ModelType.LIGHT},
        ufp_required_field=None,
        ufp_value="light_device_settings.pir_duration",
        ufp_set_function="set_duration",
    ),
    UnifiProtectNumberEntityDescription(
        key=_KEY_CHIME,
        name="Duration",
        icon="mdi:camera-timer",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_min=0,
        ufp_max=10000,
        ufp_step=100,
        ufp_device_types=DEVICES_WITH_CAMERA,
        ufp_required_field="feature_flags.has_chime",
        ufp_value="chime_duration",
        ufp_set_function="set_chime_duration",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up Select entities for UniFi Protect integration."""
    entry_data: UnifiProtectEntryData = hass.data[DOMAIN][entry.entry_id]
    protect = entry_data.protect
    protect_data = entry_data.protect_data

    entities = []

    for description in NUMBER_TYPES:
        for device in protect_data.get_by_types(description.ufp_device_types):
            if description.ufp_required_field:
                required_field = get_nested_attr(device, description.ufp_required_field)
                if not required_field:
                    continue

            entities.append(
                UnifiProtectNumbers(
                    protect,
                    protect_data,
                    device,
                    description,
                )
            )
            _LOGGER.debug(
                "Adding number entity %s for %s",
                description.name,
                device.name,
            )

    if not entities:
        return

    async_add_entities(entities)


class UnifiProtectNumbers(UnifiProtectEntity, NumberEntity):
    """A Unifi Protect Number Entity."""

    def __init__(
        self,
        protect,
        protect_data,
        device,
        description: UnifiProtectNumberEntityDescription,
    ):
        """Initialize the Number Entities."""
        super().__init__(protect, protect_data, device, description)
        self._attr_name = f"{self.device.name} {self.entity_description.name}"
        self._attr_max_value = self.entity_description.ufp_max
        self._attr_min_value = self.entity_description.ufp_min
        self._attr_step = self.entity_description.ufp_step

    @property
    def state(self) -> float:
        """Return the state of the sensor."""
        value = get_nested_attr(self.device, self.entity_description.ufp_value)

        if self.entity_description.key == _KEY_DURATION:
            value = value.total_seconds()

        return value

    async def async_set_value(self, value: float) -> None:
        """Set new value."""
        function = self.entity_description.ufp_set_function
        _LOGGER.debug(
            "Calling %s to set %s for Camera %s",
            function,
            value,
            self.device.name,
        )

        if self.entity_description.key == _KEY_DURATION:
            value = timedelta(seconds=value)

        await getattr(self.device, function)(value)
