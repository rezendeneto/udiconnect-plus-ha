"""Binary sensors for Udiconnect Plus."""

import logging
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    entities = []
    for device in coordinator.data:
        entities.append(UdiconnectBatteryLow(coordinator, device))
        entities.append(UdiconnectConnectivity(coordinator, device))
    async_add_entities(entities)


class _UdiconnectBinarySensor(CoordinatorEntity, BinarySensorEntity):
    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, device):
        super().__init__(coordinator)
        self._device_id = device.get("device_id")

    def _current_device(self) -> dict:
        for device in self.coordinator.data:
            if device.get("device_id") == self._device_id:
                return device
        return {}

    @property
    def device_info(self):
        device = self._current_device()
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": device.get("device_description", "Blind"),
            "manufacturer": "Udinese / Udiconnect Plus",
            "model": device.get("device_model", "Unknown"),
            "sw_version": device.get("device_firmware_version", "Unknown"),
        }


class UdiconnectBatteryLow(_UdiconnectBinarySensor):
    _attr_device_class = BinarySensorDeviceClass.BATTERY

    def __init__(self, coordinator, device):
        super().__init__(coordinator, device)
        self._attr_unique_id = f"udiconnect_plus_{self._device_id}_low_battery"
        self._attr_name = "Bateria fraca"

    @property
    def is_on(self) -> bool:
        return self._current_device().get("low_battery", False)


class UdiconnectConnectivity(_UdiconnectBinarySensor):
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, coordinator, device):
        super().__init__(coordinator, device)
        self._attr_unique_id = f"udiconnect_plus_{self._device_id}_connectivity"
        self._attr_name = "Online"

    @property
    def is_on(self) -> bool:
        return self._current_device().get("is_online", True)
