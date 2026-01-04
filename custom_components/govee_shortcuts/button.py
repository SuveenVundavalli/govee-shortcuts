import logging
import httpx
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    api_key = hass.data[DOMAIN][entry.entry_id]
    
    # In a real scenario, we'd fetch these from the API if discovery worked.
    # Since we found "BaseGroup" devices in the device list act as the shortcuts/scenes,
    # we'll fetch the device list and filter for BaseGroup or specific scene-capable devices.
    
    buttons = []
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://openapi.api.govee.com/router/api/v1/user/devices",
                headers={"Govee-API-Key": api_key},
                timeout=10
            )
            if response.status_code == 200:
                devices = response.json().get("data", [])
                for dev in devices:
                    # Govee shortcuts/groups often appear as "BaseGroup"
                    # or specific snapshots in the capabilities.
                    if dev.get("sku") == "BaseGroup":
                        buttons.append(GoveeShortcutButton(api_key, dev))
                    
                    # Also check for Snapshots which are common for Dreamview
                    for cap in dev.get("capabilities", []):
                        if cap.get("instance") == "snapshot":
                            options = cap.get("parameters", {}).get("options", [])
                            for opt in options:
                                buttons.append(GoveeSnapshotButton(api_key, dev, opt))
        except Exception as e:
            _LOGGER.error("Error fetching Govee devices: %s", e)

    async_add_entities(buttons)

class GoveeShortcutButton(ButtonEntity):
    def __init__(self, api_key, device_data):
        self._api_key = api_key
        self._device = device_data["device"]
        self._attr_name = f"Govee Shortcut: {device_data['deviceName']}"
        self._attr_unique_id = f"govee_shortcut_{self._device}"

    async def async_press(self) -> None:
        async with httpx.AsyncClient() as client:
            payload = {
                "requestId": "ha_button_press",
                "payload": {
                    "sku": "BaseGroup",
                    "device": self._device,
                    "capability": {
                        "type": "devices.capabilities.on_off",
                        "instance": "powerSwitch",
                        "value": 1
                    }
                }
            }
            await client.post(
                "https://openapi.api.govee.com/router/api/v1/device/control",
                headers={"Govee-API-Key": self._api_key, "Content-Type": "application/json"},
                json=payload
            )

class GoveeSnapshotButton(ButtonEntity):
    def __init__(self, api_key, device_data, option):
        self._api_key = api_key
        self._sku = device_data["sku"]
        self._device = device_data["device"]
        self._value = option["value"]
        self._attr_name = f"Govee Scene: {device_data['deviceName']} {option['name']}"
        self._attr_unique_id = f"govee_scene_{self._device}_{self._value}"

    async def async_press(self) -> None:
        async with httpx.AsyncClient() as client:
            payload = {
                "requestId": "ha_scene_press",
                "payload": {
                    "sku": self._sku,
                    "device": self._device,
                    "capability": {
                        "type": "devices.capabilities.dynamic_scene",
                        "instance": "snapshot",
                        "value": self._value
                    }
                }
            }
            await client.post(
                "https://openapi.api.govee.com/router/api/v1/device/control",
                headers={"Govee-API-Key": self._api_key, "Content-Type": "application/json"},
                json=payload
            )
