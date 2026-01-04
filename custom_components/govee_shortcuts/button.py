import logging
import httpx
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN, CONF_API_KEY, CONF_WHITELIST

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    config = data["config"]
    client = data["client"]
    
    api_key = config[CONF_API_KEY]
    whitelist_str = config.get(CONF_WHITELIST, "")
    whitelist = [item.strip().lower() for item in whitelist_str.split(",") if item.strip()]
    
    def is_whitelisted(name: str) -> bool:
        """Check if a name matches any keyword in the whitelist. If whitelist is empty, allow all."""
        if not whitelist:
            return True
        return any(keyword in name.lower() for keyword in whitelist)

    buttons = []

    try:
        # 1. Fetch Device List (includes Groups and physical lights)
        resp = await client.get(
            "https://openapi.api.govee.com/router/api/v1/user/devices",
            headers={"Govee-API-Key": api_key}
        )
        if resp.status_code != 200:
            _LOGGER.error("Failed to fetch devices: %s", resp.text)
            return
        
        devices = resp.json().get("data", [])
        for dev in devices:
            sku = dev.get("sku")
            device_id = dev.get("device")
            device_name = dev.get("deviceName")

            # Handle BaseGroups (Commonly where "Rainbow", "Candle Lights AI" reside)
            if sku == "BaseGroup":
                if is_whitelisted(device_name):
                    buttons.append(GoveeShortcutButton(client, api_key, dev))
                continue

            # 2. Check for "Snapshot" capability directly in the device list
            for cap in dev.get("capabilities", []):
                if cap.get("instance") == "snapshot":
                    options = cap.get("parameters", {}).get("options", [])
                    for opt in options:
                        if is_whitelisted(opt["name"]):
                            buttons.append(GoveeSceneButton(
                                client, api_key, sku, device_id, device_name, "snapshot", opt
                            ))

            # 3. Check DIY Scenes
            diy_resp = await client.post(
                "https://openapi.api.govee.com/router/api/v1/device/diy-scenes",
                headers={"Govee-API-Key": api_key, "Content-Type": "application/json"},
                json={
                    "requestId": f"ha_diy_disc_{device_id}",
                    "payload": {"sku": sku, "device": device_id}
                }
            )
            
            if diy_resp.status_code == 200:
                diy_data = diy_resp.json().get("payload", {})
                for cap in diy_data.get("capabilities", []):
                    options = cap.get("parameters", {}).get("options", [])
                    for opt in options:
                        if is_whitelisted(opt["name"]):
                            buttons.append(GoveeSceneButton(
                                client, api_key, sku, device_id, device_name, "diyScene", opt
                            ))

            # 4. Filtered Scene Check
            scene_resp = await client.post(
                "https://openapi.api.govee.com/router/api/v1/device/scenes",
                headers={"Govee-API-Key": api_key, "Content-Type": "application/json"},
                json={
                    "requestId": f"ha_scene_disc_{device_id}",
                    "payload": {"sku": sku, "device": device_id}
                }
            )
            
            if scene_resp.status_code == 200:
                scene_data = scene_resp.json().get("payload", {})
                for cap in scene_data.get("capabilities", []):
                    if cap.get("instance") == "lightScene":
                        options = cap.get("parameters", {}).get("options", [])
                        for opt in options:
                            if is_whitelisted(opt["name"]):
                                buttons.append(GoveeSceneButton(
                                    client, api_key, sku, device_id, device_name, "lightScene", opt
                                ))
            
    except Exception as e:
        _LOGGER.error("Error during Govee discovery: %s", e)

    async_add_entities(buttons)

class GoveeShortcutButton(ButtonEntity):
    """Buttons for BaseGroups (Group Control)."""
    _attr_icon = "mdi:gesture-tap-button"

    def __init__(self, client, api_key, device_data):
        self._client = client
        self._api_key = api_key
        self._device = device_data["device"]
        self._attr_name = f"Govee Shortcut: {device_data['deviceName']}"
        self._attr_unique_id = f"govee_shortcut_{self._device}"

    async def async_press(self) -> None:
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
        await self._client.post(
            "https://openapi.api.govee.com/router/api/v1/device/control",
            headers={"Govee-API-Key": self._api_key, "Content-Type": "application/json"},
            json=payload
        )

class GoveeSceneButton(ButtonEntity):
    """Buttons for specific whitelisted device scenes (DIY, Snapshot, or LightScene)."""
    _attr_icon = "mdi:palette"

    def __init__(self, client, api_key, sku, device, device_name, instance, option):
        self._client = client
        self._api_key = api_key
        self._sku = sku
        self._device = device
        self._instance = instance
        self._value = option["value"]
        self._attr_name = f"Govee Scene: {device_name} {option['name']}"
        self._attr_unique_id = f"govee_scene_{device}_{instance}_{option['name']}"

    async def async_press(self) -> None:
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
        await self._client.post(
            "https://openapi.api.govee.com/router/api/v1/device/control",
            headers={"Govee-API-Key": self._api_key, "Content-Type": "application/json"},
            json=payload
        )
