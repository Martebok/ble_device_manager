from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.const import PERCENTAGE
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_ADDRESS, DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([BLEBatterySensor(coordinator, entry)])


class BLEBatterySensor(CoordinatorEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._address = entry.data["address"]
        self._attr_name = f"{entry.data['name']} Batteria"
        self._attr_unique_id = f"{self._address}_battery"

    @property
    def native_value(self):
        device = self.coordinator.devices.get(self._address)
        if device is None:
            return None
        return device.get("battery")