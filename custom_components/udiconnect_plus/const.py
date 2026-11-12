"""Constants for Udiconnect Plus integration."""

DOMAIN = "udiconnect_plus"

# API Configuration
BASE_URL = "https://api.connectservices.assaabloy.com/api/YaleConnect"
BRAND_PLATFORM_GUID = (
    "883fe30e-6df9-4cc8-954c-f91aa9dadac5.3939e0f2-08e5-4bb1-b3a6-ddb1183666d3"
)

# Configuration
CONF_EMAIL = "E-Mail"
CONF_PASSWORD = "Password"

# Default values
# Every poll is a full account sync against the vendor cloud; at 10 s the cloud
# answered with intermittent 500/503s. Commands trigger an immediate refresh anyway.
DEFAULT_SCAN_INTERVAL = 60  # seconds
REQUEST_TIMEOUT = 15  # seconds; requests has no default, so a stalled call hung forever

# Attributes
ATTR_DEVICE_ID = "device_id"
ATTR_HOME_ID = "home_id"
ATTR_DEVICE_MODEL = "device_model"
