import logging
import httpx
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    api_key = hass.data[DOMAIN][entry.entry_id]
    buttons = []

    async with httpx.AsyncClient() as client:
        try:
            # 1. Fetch Device List
            resp = await client.get(
                "https://openapi.api.govee.com/router/api/v1/user/devices",
                headers={"Govee-API-Key": api_key},
                timeout=10
            )
            if resp.status_code != 200:
                _LOGGER.error("Failed to fetch devices: %s", resp.text)
                return
            
            devices = resp.json().get("data", [])
            for dev in devices:
                sku = dev.get("sku")
                device_id = dev.get("device")
                device_name = dev.get("deviceName")

                # Handle BaseGroups (Commonly used for Tap-to-Run style control)
                if sku == "BaseGroup":
                    buttons.append(GoveeShortcutButton(api_key, dev))
                    continue

                # 2. Fetch Scenes for each device
                # The device list often has empty options for lightScene, 
                # we need to query the dedicated endpoint.
                scene_resp = await client.post(
                    "https://openapi.api.govee.com/router/api/v1/device/scenes",
                    headers={"Govee-API-Key": api_key, "Content-Type": "application/json"},
                    json={
                        "requestId": f"ha_scene_disc_{device_id}",
                        "payload": {"sku": sku, "device": device_id}
                    },
                    timeout=10
                )
                
                if scene_resp.status_code == 200:
                    scene_data = scene_resp.json().get("payload", {})
                    for cap in scene_data.get("capabilities", []):
                        if cap.get("instance") in ["lightScene", "snapshot", "diyScene"]:
                            options = cap.get("parameters", {}).get("options", [])
                            for opt in options:
                                buttons.append(GoveeSceneButton(
                                    api_key, sku, device_id, device_name, cap["instance"], opt
                                ))
                
        except Exception as e:
            _LOGGER.error("Error during Govee discovery: %s", e)

    async_add_entities(buttons)

class GoveeShortcutButton(ButtonEntity):
    """Buttons for BaseGroups (Group Control)."""
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

class GoveeSceneButton(ButtonEntity):
    """Buttons for specific device scenes (Sunrise, Movie, etc)."""
    def __init__(self, api_key, sku, device, device_name, instance, option):
        self._api_key = api_key
        self._sku = sku
        self._device = device
        self._instance = instance
        self._value = option["value"]
        self._attr_name = f"Govee Scene: {device_name} {option['name']}"
        self._attr_unique_id = f"govee_scene_{device}_{instance}_{option['name']}"

    async def async_press(self) -> None:
        async with httpx.AsyncClient() as client:
            payload = {
                "requestId": "ha_scene_press",
                "payload": {
                    "sku": self._sku,
                    "device": self._device,
                    "capability": {
                        "type": "devices.capabilities.dynamic_scene",
                        "instance": self._instance,
                        "value": self._value
                    }
                }
            }
            _LOGGER.debug("Triggering Govee Scene: %s", payload)
            await client.post(
                "https://openapi.api.govee.com/router/api/v1/device/control",
                headers={"Govee-API-Key": self._api_key, "Content-Type": "application/json"},
                json=payload
            )
