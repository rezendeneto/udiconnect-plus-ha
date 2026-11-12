"""Udiconnect Plus API Client."""

import logging
import threading
import requests
from typing import Any, Dict, List, Optional

from .const import BASE_URL, BRAND_PLATFORM_GUID, REQUEST_TIMEOUT

_LOGGER = logging.getLogger(__name__)


class UdiconnectPlusError(Exception):
    """Raised when the Udiconnect Plus cloud does not complete a request."""


class UdiconnectPlusAPI:
    """Udiconnect Plus API Client."""

    def __init__(self, email: str, password: str):
        """Initialize the API client."""
        self.email = email
        self.password = password
        self.access_token: Optional[str] = None
        self.session = requests.Session()
        # The coordinator poll and cover commands run in different executor
        # threads; serialize them so a re-login cannot race a request.
        self._lock = threading.Lock()

    def _get_headers(self, authenticated: bool = True) -> Dict[str, str]:
        """Get request headers."""
        headers = {
            "Content-Type": "application/json",
            "brandPlatformGUID": BRAND_PLATFORM_GUID,
        }
        if authenticated and self.access_token:
            headers["access-token"] = self.access_token
        return headers

    # API Endpoints
    def login(self) -> bool:
        """Login and get access token."""

        url = f"{BASE_URL}/Account/Login"
        headers = self._get_headers(authenticated=False)

        payload = {
            "email": self.email,
            "password": self.password,
            "mobileInformation": {
                "os": "Android 13",
                "information": "Samsung SM-G998B",
                "appVersion": "4.8.8",
                "pushToken": "fcm_token",
                "UUID": "device-uuid",
            },
        }

        try:
            response = self.session.post(
                url, headers=headers, json=payload, timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()

            data = response.json()
            self.access_token = data.get("accessToken")

            if self.access_token:
                _LOGGER.info("Successfully logged in to Udiconnect Plus")
                return True
            else:
                _LOGGER.error("No access token in login response")
                return False

        except (requests.exceptions.RequestException, ValueError) as err:
            _LOGGER.error("Login failed: %s", err)
            return False

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """POST an authenticated request, logging in again and retrying once.

        The access token from login() expires or gets revoked server-side, and
        the cloud does not report that with a consistent status (404 and 500
        have both been seen), so any failure triggers one fresh login and one
        retry before giving up.
        """
        url = f"{BASE_URL}/{path}"
        with self._lock:
            last_err: Optional[Exception] = None
            for attempt in (1, 2):
                if attempt == 2 or not self.access_token:
                    if not self.login():
                        raise UdiconnectPlusError(f"{path}: login failed") from last_err
                try:
                    response = self.session.post(
                        url,
                        headers=self._get_headers(),
                        json=payload,
                        timeout=REQUEST_TIMEOUT,
                    )
                    response.raise_for_status()
                    return response.json()
                except (requests.exceptions.RequestException, ValueError) as err:
                    last_err = err
                    _LOGGER.warning("%s failed (attempt %d of 2): %s", path, attempt, err)
            raise UdiconnectPlusError(f"{path}: {last_err}") from last_err

    def sync_account(self) -> Dict[str, Any]:
        """Sync account data and get all devices."""
        return self._post("App/SyncAccount", {})

    def set_curtain_position(self, device_id: str, position: int) -> None:
        """Set curtain to absolute position (0-100); raises UdiconnectPlusError on failure."""

        payload = {
            "action": "CurtainSetPosition",
            "deviceId": device_id,
            "position": position,
        }

        data = self._post("Curtain/SetPositionCurtain", payload)
        if data.get("result") is not True:
            raise UdiconnectPlusError(
                f"set position {position} on {device_id} refused: {data.get('message')}"
            )
        _LOGGER.debug("Set curtain %s to position %d", device_id, position)

    # Utility methods
    def get_devices(self) -> List[Dict[str, Any]]:
        """Get all devices from all homes; raises UdiconnectPlusError on failure."""

        account_data = self.sync_account()
        homes = (account_data.get("account") or {}).get("homeList")
        if not isinstance(homes, list):
            # An empty device list would silently drop every entity, so a
            # payload without homeList is a failed poll, not "no devices".
            raise UdiconnectPlusError("SyncAccount response has no homeList")

        devices = [
            {
                "home_id": home.get("homeId"),
                "home_description": home.get("description"),
                "device_id": device.get("deviceId"),
                "device_description": device.get("description"),
                "device_category": device.get("category"),
                "device_firmware_version": device.get("currentFirmwareVersion"),
                "device_position": device.get("state"),
                "device_model": device.get("deviceModelDescription"),
            }
            for home in homes
            for device in (home.get("deviceList") or [])
        ]

        _LOGGER.debug("Found %d devices", len(devices))
        return devices

    def close(self):
        """Close the session."""
        self.session.close()
