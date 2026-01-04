import logging
import httpx
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Govee Shortcuts from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Use a persistent client stored in hass.data
    # We use httpx.AsyncClient for the Govee OpenAPI
    client = httpx.AsyncClient(timeout=10)
    
    hass.data[DOMAIN][entry.entry_id] = {
        "config": entry.data,
        "client": client,
    }
    
    await hass.config_entries.async_forward_entry_setups(entry, ["button"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    data = hass.data[DOMAIN].get(entry.entry_id)
    if data and "client" in data:
        await data["client"].aclose()
        
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["button"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
