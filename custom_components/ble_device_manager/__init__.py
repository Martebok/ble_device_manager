import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import CONF_ADDRESS, CONF_NAME, CONF_THRESHOLD, DOMAIN
from .coordinator import BLEGlobalCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator: BLEGlobalCoordinator = hass.data.setdefault(DOMAIN, {}).get(entry.entry_id)
    if coordinator is None:
        coordinator = BLEGlobalCoordinator(hass)
        await coordinator.async_config_entry_first_refresh()
        hass.data[DOMAIN][entry.entry_id] = coordinator

    await coordinator.async_register_device(
        entry.data[CONF_ADDRESS],
        entry.data[CONF_NAME],
        entry.data.get(CONF_THRESHOLD, 30),
    )

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "binary_sensor"])
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor", "binary_sensor"])
    if unload_ok:
        coordinator: BLEGlobalCoordinator = hass.data[DOMAIN].pop(entry.entry_id, None)
        if coordinator is not None:
            await coordinator.async_unregister_device(entry.data[CONF_ADDRESS])
    return unload_ok