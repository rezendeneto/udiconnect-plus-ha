"""Platform for Udiconnect Plus cover integration."""

import logging
from typing import Any

from homeassistant.components.cover import (
    CoverDeviceClass,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTR_DEVICE_ID, ATTR_DEVICE_MODEL, ATTR_HOME_ID, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    api = hass.data[DOMAIN][entry.entry_id]["api"]
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities(
        UdiconnectPlusCover(coordinator, api, device) for device in coordinator.data
    )


class UdiconnectPlusCover(CoordinatorEntity, CoverEntity):
    _attr_has_entity_name = True
    _attr_name = None  # usa só o nome do device, sem duplicar
    _attr_device_class = CoverDeviceClass.BLIND
    _attr_supported_features = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.SET_POSITION
        | CoverEntityFeature.STOP
    )

    def __init__(self, coordinator, api, device):
        super().__init__(coordinator)
        self._api = api
        self._device_id = device.get("device_id")
        self._attr_unique_id = f"udiconnect_plus_device_id_{self._device_id}"

    def _current_device(self) -> dict:
        for device in self.coordinator.data:
            if device.get("device_id") == self._device_id:
                return device
        return {}

    @property
    def available(self) -> bool:
        return self._current_device().get("is_online", True)

    @property
    def device_info(self):
        device = self._current_device()
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": device.get("device_description", "Persiana"),
            "manufacturer": "Udinese / Udiconnect Plus",
            "model": device.get("device_model", "Unknown"),
            "sw_version": device.get("device_firmware_version", "Unknown"),
        }

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        device = self._current_device()
        return {
            ATTR_DEVICE_ID: self._device_id,
            ATTR_HOME_ID: device.get("home_id"),
            ATTR_DEVICE_MODEL: device.get("device_model"),
            "low_battery": device.get("low_battery", False),
            "new_firmware_available": device.get("new_firmware_available", False),
            "is_calibrating": device.get("is_calibrating", False),
        }

    @property
    def current_cover_position(self) -> int | None:
        position = self._current_device().get("device_position")
        if position is not None:
            return int(position)
        return None

    @property
    def is_closed(self) -> bool | None:
        position = self.current_cover_position
        if position is not None:
            return position == 0
        return None

    @property
    def is_opening(self) -> bool:
        return self._current_device().get("is_calibrating", False)

    @property
    def is_closing(self) -> bool:
        return False

    async def async_open_cover(self, **kwargs: Any) -> None:
        await self.hass.async_add_executor_job(
            self._api.set_curtain_position, self._device_id, 100
        )
        await self.coordinator.async_request_refresh()

    async def async_close_cover(self, **kwargs: Any) -> None:
        await self.hass.async_add_executor_job(
            self._api.set_curtain_position, self._device_id, 0
        )
        await self.coordinator.async_request_refresh()

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        position = kwargs.get("position")
        if position is not None:
            await self.hass.async_add_executor_job(
                self._api.set_curtain_position, self._device_id, position
            )
            await self.coordinator.async_request_refresh()

    async def async_stop_cover(self, **kwargs: Any) -> None:
        current = self.current_cover_position
        if current is not None:
            await self.hass.async_add_executor_job(
                self._api.set_curtain_position, self._device_id, current
            )
