"""Update entities for Udiconnect Plus."""

import logging
from homeassistant.components.update import UpdateEntity
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
    async_add_entities(
        UdiconnectFirmwareUpdate(coordinator, device) for device in coordinator.data
    )


class UdiconnectFirmwareUpdate(CoordinatorEntity, UpdateEntity):
    _attr_has_entity_name = True
    _attr_name = "Firmware"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, device):
        super().__init__(coordinator)
        self._device_id = device.get("device_id")
        self._attr_unique_id = f"udiconnect_plus_{self._device_id}_firmware"

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

    @property
    def installed_version(self) -> str | None:
        return self._current_device().get("device_firmware_version")

    @property
    def latest_version(self) -> str | None:
        device = self._current_device()
        if device.get("new_firmware_available"):
            return "Nova versão disponível"
        return self.installed_version
