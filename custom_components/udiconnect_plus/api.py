"""Udiconnect Plus API Client."""

from functools import reduce
import logging
import requests
from typing import Any, Dict, List, Optional

from .const import BASE_URL, BRAND_PLATFORM_GUID

_LOGGER = logging.getLogger(__name__)


class UdiconnectPlusAPI:
    """Udiconnect Plus API Client."""

    def __init__(self, email: str, password: str):
        """Initialize the API client."""
        self.email = email
        self.password = password
        self.access_token: Optional[str] = None
        self.session = requests.Session()

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
            response = self.session.post(url, headers=headers, json=payload)
            response.raise_for_status()

            data = response.json()
            self.access_token = data.get("accessToken")

            if self.access_token:
                _LOGGER.info("Successfully logged in to Udiconnect Plus")
                return True
            else:
                _LOGGER.error("No access token in login response")
                return False

        except requests.exceptions.RequestException as err:
            _LOGGER.error("Login failed: %s", err)
            return False

    def sync_account(self) -> Optional[Dict[str, Any]]:
        """Sync account data and get all devices."""

        url = f"{BASE_URL}/App/SyncAccount"
        headers = self._get_headers()

        try:
            response = self.session.post(url, headers=headers, json={})
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as err:
            _LOGGER.error("Sync account failed: %s", err)
            return None

    def set_curtain_position(self, device_id: str, position: int) -> bool:
        """Set curtain to absolute position (0-100)."""

        headers = self._get_headers()
        url = f"{BASE_URL}/Curtain/SetPositionCurtain"

        payload = {
            "action": "CurtainSetPosition",
            "deviceId": device_id,
            "position": position,
        }

        try:
            response = self.session.post(url, headers=headers, json=payload)
            response.raise_for_status()

            data = response.json()

            if data.get("result") == True:
                _LOGGER.debug("Set curtain %s to position %d", device_id, position)
                return True
            else:
                _LOGGER.error("Failed to set curtain position: %s", data.get("message"))
                return False

        except requests.exceptions.RequestException as err:
            _LOGGER.error("Failed to set curtain position: %s", err)
            return None

    # Utility methods
    def get_devices(self) -> List[Dict[str, Any]]:
        """Get all devices from all homes."""

        account_data = self.sync_account()
        if not account_data:
            return []

        devices = reduce(
            lambda a, b: a
            + list(
                map(
                    lambda x: {
                        "home_id": b.get("homeId"),
                        "home_description": b.get("description"),
                        "device_id": x.get("deviceId"),
                        "device_description": x.get("description"),
                        "device_category": x.get("category"),
                        "device_firmware_version": x.get("currentFirmwareVersion"),
                        "device_position": x.get("state"),
                        "device_model": x.get("deviceModelDescription"),
                    },
                    b.get("deviceList"),
                )
            ),
            account_data.get("account").get("homeList"),
            [],
        )

        _LOGGER.info("Found %d devices", len(devices))
        return devices

    def close(self):
        """Close the session."""
        self.session.close()
