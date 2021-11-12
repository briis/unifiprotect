"""This component provides number entities for Unifi Protect."""
from dataclasses import dataclass
import logging

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DEVICES_WITH_CAMERA, DOMAIN, ENTITY_CATEGORY_CONFIG
from .data import UnifiProtectData
from .entity import UnifiProtectEntity

_LOGGER = logging.getLogger(__name__)

_ENTITY_WDR = "wdr_value"
_ENTITY_MIC_LEVEL = "mic_level"
_ENTITY_ZOOM_POS = "zoom_position"


@dataclass
class UnifiprotectRequiredKeysMixin:
    """Mixin for required keys."""

    ufp_max: int
    ufp_min: int
    ufp_step: int
    ufp_device_type: str
    ufp_required_field: str
    ufp_value: str
    ufp_set_function: str


@dataclass
class UnifiProtectNumberEntityDescription(
    NumberEntityDescription, UnifiprotectRequiredKeysMixin
):
    """Describes Unifi Protect Number entity."""


NUMBER_TYPES: tuple[UnifiProtectNumberEntityDescription, ...] = (
    UnifiProtectNumberEntityDescription(
        key=_ENTITY_WDR,
        name="Wide Dynamic Range",
        icon="mdi:state-machine",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_min=0,
        ufp_max=3,
        ufp_step=1,
        ufp_device_type=DEVICES_WITH_CAMERA,
        ufp_required_field=None,
        ufp_value="wdr",
        ufp_set_function="set_camera_wdr",
    ),
    UnifiProtectNumberEntityDescription(
        key=_ENTITY_MIC_LEVEL,
        name="Microphone Level",
        icon="mdi:microphone",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_min=0,
        ufp_max=100,
        ufp_step=1,
        ufp_device_type=DEVICES_WITH_CAMERA,
        ufp_required_field=None,
        ufp_value="mic_volume",
        ufp_set_function="set_mic_volume",
    ),
    UnifiProtectNumberEntityDescription(
        key=_ENTITY_ZOOM_POS,
        name="Zoom Position",
        icon="mdi:magnify-plus-outline",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_min=0,
        ufp_max=100,
        ufp_step=1,
        ufp_device_type=DEVICES_WITH_CAMERA,
        ufp_required_field="has_opticalzoom",
        ufp_value="zoom_position",
        ufp_set_function="set_camera_zoom_position",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up Select entities for UniFi Protect integration."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    upv_object = entry_data["upv"]
    protect_data: UnifiProtectData = entry_data["protect_data"]
    server_info = entry_data["server_info"]
    if not protect_data.data:
        return

    entities = []

    for description in NUMBER_TYPES:
        for device_id, device_data in protect_data.data.items():
            if device_data.get("type") not in description.ufp_device_type:
                continue

            if description.ufp_required_field and not device_data.get(
                description.ufp_required_field
            ):
                continue

            entities.append(
                UnifiProtectNumbers(
                    upv_object,
                    protect_data,
                    server_info,
                    device_id,
                    description,
                )
            )
            _LOGGER.debug(
                "Adding number entity %s for %s",
                description.name,
                device_data.get("name"),
            )

    if not entities:
        return

    async_add_entities(entities)


class UnifiProtectNumbers(UnifiProtectEntity, NumberEntity):
    """A Unifi Protect Number Entity."""

    def __init__(
        self,
        upv_object,
        protect_data,
        server_info,
        device_id,
        description: UnifiProtectNumberEntityDescription,
    ):
        """Initialize the Number Entities."""
        super().__init__(upv_object, protect_data, server_info, device_id, description)
        self._name = f"{self.entity_description.name} {self._device_data['name']}"
        self._device_type = self.entity_description.ufp_device_type
        self._attr_max_value = self.entity_description.ufp_max
        self._attr_min_value = self.entity_description.ufp_min
        self._attr_step = self.entity_description.ufp_step

    @property
    def name(self):
        """Return name of the entity."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._device_data[self.entity_description.ufp_value]

    async def async_set_value(self, value: float) -> None:
        """Set new value."""
        function = self.entity_description.ufp_set_function
        _LOGGER.debug(
            "Calling %s to set %s for Camera %s",
            function,
            value,
            self._device_data["name"],
        )
        await getattr(self.upv_object, function)(self._device_id, value)
