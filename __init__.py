"""Udiconnect Plus integration for Home Assistant."""

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import UdiconnectPlusAPI
from .const import CONF_EMAIL, CONF_PASSWORD, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.COVER]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Udiconnect Plus from a config entry."""
    email = entry.data[CONF_EMAIL]
    password = entry.data[CONF_PASSWORD]

    api = UdiconnectPlusAPI(email, password)

    # Login in executor since it's blocking I/O
    login_success = await hass.async_add_executor_job(api.login)

    if not login_success:
        _LOGGER.error("Failed to login to Udiconnect Plus")
        return False

    async def async_update_data():
        """Fetch data from API."""
        try:
            devices = await hass.async_add_executor_job(api.get_devices)
            return devices
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=async_update_data,
        update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
    )

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        api = hass.data[DOMAIN][entry.entry_id]["api"]
        await hass.async_add_executor_job(api.close)
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
