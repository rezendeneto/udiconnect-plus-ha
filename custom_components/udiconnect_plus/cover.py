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
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import UdiconnectPlusError
from .const import (
    ATTR_DEVICE_ID,
    ATTR_DEVICE_MODEL,
    ATTR_HOME_ID,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Udiconnect Plus covers from a config entry."""
    api = hass.data[DOMAIN][entry.entry_id]["api"]
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities = [
        UdiconnectPlusCover(coordinator, api, device) for device in coordinator.data
    ]

    async_add_entities(entities)


class UdiconnectPlusCover(CoordinatorEntity, CoverEntity):
    """Representation of a Udiconnect Plus curtain/blind."""

    _attr_has_entity_name = True
    _attr_device_class = CoverDeviceClass.BLIND
    _attr_supported_features = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.SET_POSITION
    )

    def __init__(self, coordinator, api, device):
        """Initialize the cover."""
        super().__init__(coordinator)
        self._api = api
        self._device = device
        self._attr_unique_id = f"udiconnect_plus_device_id_{device.get('device_id')}"
        self._attr_name = device.get("device_description", "Blind")

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._device.get("device_id"))},
            "name": self._attr_name,
            "manufacturer": "Udiconnect Plus",
            "model": self._device.get("device_model", "Unknown"),
            "sw_version": self._device.get("device_firmware_version", "Unknown"),
        }

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        return {
            ATTR_DEVICE_ID: self._device.get("device_id"),
            ATTR_HOME_ID: self._device.get("home_id"),
            ATTR_DEVICE_MODEL: self._device.get("device_description"),
        }

    @property
    def current_cover_position(self) -> int | None:
        """Return current position of cover (0 closed, 100 open)."""
        # Update device data from coordinator
        for device in self.coordinator.data:
            if device.get("device_id") == self._device.get("device_id"):
                self._device = device
                break

        # The cloud has been seen returning non-numeric and out-of-range states;
        # report those as unknown instead of crashing or showing a bogus position.
        try:
            position = int(self._device.get("device_position"))
        except (TypeError, ValueError):
            return None
        if 0 <= position <= 100:
            return position
        return None

    @property
    def is_closed(self) -> bool | None:
        """Return if the cover is closed."""
        position = self.current_cover_position
        if position is not None:
            return position == 0
        return None

    async def _async_set_position(self, position: int) -> None:
        """Send a position and surface cloud failures to the caller."""
        try:
            await self.hass.async_add_executor_job(
                self._api.set_curtain_position, self._device.get("device_id"), position
            )
        except UdiconnectPlusError as err:
            # Raising makes the service call fail visibly, so scripts and
            # automations can retry or notify instead of assuming it moved.
            raise HomeAssistantError(f"{self.name}: {err}") from err
        finally:
            await self.coordinator.async_request_refresh()

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open the cover."""
        await self._async_set_position(100)

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Close the cover."""
        await self._async_set_position(0)

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        """Move the cover to a specific position."""
        position = kwargs.get("position")
        if position is not None:
            await self._async_set_position(position)
