""" This component provides binary sensors for Unifi Protect."""
import logging
import voluptuous as vol

import homeassistant.helpers.config_validation as cv

try:
    from homeassistant.components.binary_sensor import (
        BinarySensorEntity as BinarySensorDevice,
    )
except ImportError:
    # Prior to HA v0.110
    from homeassistant.components.binary_sensor import BinarySensorDevice

from homeassistant.components.binary_sensor import DEVICE_CLASS_MOTION
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    ATTR_LAST_TRIP_TIME,
    CONF_ID,
)
import homeassistant.helpers.device_registry as dr
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.util import slugify
from .const import (
    ATTR_EVENT_SCORE,
    DOMAIN,
    DEFAULT_ATTRIBUTION,
    DEFAULT_BRAND,
    DEVICE_CLASS_DOORBELL,
    ENTITY_ID_BINARY_SENSOR_FORMAT,
    ENTITY_UNIQUE_ID,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistantType, entry: ConfigEntry, async_add_entities
) -> None:
    """A Ubiquiti Unifi Protect Binary Sensor."""
    coordinator = hass.data[DOMAIN][entry.data[CONF_ID]]["coordinator"]
    if not coordinator.data:
        return

    sensors = []
    for camera in coordinator.data:
        if coordinator.data[camera]["type"] == DEVICE_CLASS_DOORBELL:
            sensors.append(
                UnifiProtectBinarySensor(
                    coordinator, camera, DEVICE_CLASS_DOORBELL, entry.data[CONF_ID]
                )
            )
            _LOGGER.debug(
                f"UNIFIPROTECT DOORBELL SENSOR CREATED: {coordinator.data[camera]['name']}"
            )

        sensors.append(
            UnifiProtectBinarySensor(
                coordinator, camera, DEVICE_CLASS_MOTION, entry.data[CONF_ID]
            )
        )
        _LOGGER.debug(
            f"UNIFIPROTECT MOTION SENSOR CREATED: {coordinator.data[camera]['name']}"
        )

    async_add_entities(sensors, True)

    return True


class UnifiProtectBinarySensor(BinarySensorDevice):
    """A Unifi Protect Binary Sensor."""

    def __init__(self, coordinator, camera, sensor_type, instance):
        self.coordinator = coordinator
        self._camera_id = camera
        self._camera = coordinator.data[camera]
        self._name = f"{sensor_type.capitalize()} {self._camera['name']}"
        self._mac = self._camera["mac"]
        self._firmware_version = self._camera["firmware_version"]
        self._server_id = self._camera["server_id"]
        self._camera_type = self._camera["type"]
        self._device_class = sensor_type
        self._event_score = self._camera["event_score"]
        self.entity_id = ENTITY_ID_BINARY_SENSOR_FORMAT.format(
            slugify(instance), slugify(self._name).replace(" ", "_")
        )
        self._unique_id = ENTITY_UNIQUE_ID.format(sensor_type, self._mac)

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def name(self):
        """Return name of the sensor."""
        return self._name

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        if self._device_class == DEVICE_CLASS_DOORBELL:
            return self.coordinator.data[self._camera_id]["event_ring_on"]
        else:
            return self.coordinator.data[self._camera_id]["event_on"]

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return self._device_class

    @property
    def icon(self):
        """Select icon to display in Frontend."""
        if self._device_class == DEVICE_CLASS_DOORBELL:
            if self.coordinator.data[self._camera_id]["event_ring_on"]:
                return "mdi:bell-ring-outline"
            else:
                return "mdi:doorbell-video"

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        return {
            ATTR_ATTRIBUTION: DEFAULT_ATTRIBUTION,
            ATTR_LAST_TRIP_TIME: self.coordinator.data[self._camera_id]["last_ring"]
            if self._device_class == DEVICE_CLASS_DOORBELL
            else self.coordinator.data[self._camera_id]["last_motion"],
            ATTR_EVENT_SCORE: self.coordinator.data[self._camera_id]["last_ring"]
            if self._device_class != DEVICE_CLASS_DOORBELL
            else None,
        }

    @property
    def should_poll(self):
        """No need to poll. Coordinator notifies entity of updates."""
        return False

    @property
    def available(self):
        """Return if entity is available."""
        return self.coordinator.last_update_success

    @property
    def device_info(self):
        return {
            "connections": {(dr.CONNECTION_NETWORK_MAC, self._mac)},
            "name": self.name,
            "manufacturer": DEFAULT_BRAND,
            "model": self._camera_type,
            "sw_version": self._firmware_version,
            "via_device": (DOMAIN, self._server_id),
        }

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
