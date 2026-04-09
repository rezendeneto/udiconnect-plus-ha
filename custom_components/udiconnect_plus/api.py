"""Udiconnect Plus API Client."""

from functools import reduce
import logging
import requests
from typing import Any, Dict, List, Optional

from .const import BASE_URL, BRAND_PLATFORM_GUID

_LOGGER = logging.getLogger(__name__)

_LOGIN_PAYLOAD = {
    "mobileInformation": {
        "os": "Android 13",
        "information": "Samsung SM-G998B",
        "appVersion": "4.8.8",
        "pushToken": "fcm_token",
        "UUID": "device-uuid",
    }
}


class UdiconnectPlusAPI:
    """Udiconnect Plus API Client."""

    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.access_token: Optional[str] = None
        self.session = requests.Session()

    def _get_headers(self, authenticated: bool = True) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "brandPlatformGUID": BRAND_PLATFORM_GUID,
        }
        if authenticated and self.access_token:
            headers["access-token"] = self.access_token
        return headers

    def login(self) -> bool:
        """Login and get access token."""
        url = f"{BASE_URL}/Account/Login"
        payload = {
            "email": self.email,
            "password": self.password,
            **_LOGIN_PAYLOAD,
        }
        try:
            response = self.session.post(
                url, headers=self._get_headers(authenticated=False), json=payload
            )
            response.raise_for_status()
            self.access_token = response.json().get("accessToken")
            if self.access_token:
                _LOGGER.info("Logged in to Udiconnect Plus")
                return True
            _LOGGER.error("No access token in login response")
            return False
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Login failed: %s", err)
            return False

    def _post(self, path: str, payload: dict) -> Optional[dict]:
        """POST with automatic token refresh on 401."""
        url = f"{BASE_URL}{path}"
        for attempt in range(2):
            try:
                response = self.session.post(
                    url, headers=self._get_headers(), json=payload, timeout=10
                )
                if response.status_code == 401 and attempt == 0:
                    _LOGGER.warning("Token expired, re-logging in")
                    if self.login():
                        continue
                    return None
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as err:
                _LOGGER.error("Request to %s failed: %s", path, err)
                return None
        return None

    def sync_account(self) -> Optional[Dict[str, Any]]:
        """Sync account data and get all devices."""
        return self._post("/App/SyncAccount", {})

    def set_curtain_position(self, device_id: str, position: int) -> bool:
        """Set curtain to absolute position (0-100)."""
        data = self._post(
            "/Curtain/SetPositionCurtain",
            {"action": "CurtainSetPosition", "deviceId": device_id, "position": position},
        )
        if data and data.get("result") is True:
            _LOGGER.debug("Set curtain %s to position %d", device_id, position)
            return True
        _LOGGER.error("Failed to set curtain %s position: %s", device_id, data)
        return False

    def get_devices(self) -> List[Dict[str, Any]]:
        """Get all devices from all homes."""
        account_data = self.sync_account()
        if not account_data:
            return []

        devices = reduce(
            lambda acc, home: acc + [
                {
                    "home_id": home.get("homeId"),
                    "home_description": home.get("description"),
                    "device_id": x.get("deviceId"),
                    "device_description": x.get("description"),
                    "device_category": x.get("category"),
                    "device_firmware_version": x.get("currentFirmwareVersion"),
                    "device_position": x.get("state"),
                    "device_model": x.get("deviceModelDescription"),
                    "is_online": x.get("isOnline", True),
                    "is_calibrating": x.get("isCalibrating", False),
                    "low_battery": x.get("lowBattery", False),
                    "new_firmware_available": x.get("newFirmwareAvailable", False),
                }
                for x in home.get("deviceList", [])
            ],
            account_data.get("account", {}).get("homeList", []),
            [],
        )

        _LOGGER.debug("Found %d devices", len(devices))
        return devices

    def close(self):
        self.session.close()
