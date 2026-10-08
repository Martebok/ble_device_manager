from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_ADDRESS, DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        BLEPresenceSensor(coordinator, entry),
        BLENeedsChargeSensor(coordinator, entry),
    ])


class BLEPresenceSensor(CoordinatorEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._address = entry.data["address"]
        self._attr_name = f"{entry.data['name']} Presenza"
        self._attr_unique_id = f"{self._address}_presence"

    @property
    def is_on(self):
        device = self.coordinator.devices.get(self._address)
        if device is None:
            return False
        return device.get("present", False)


class BLENeedsChargeSensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._address = entry.data["address"]
        self._attr_name = f"{entry.data['name']} Da Ricaricare"
        self._attr_unique_id = f"{self._address}_needs_charge"
        self._threshold = entry.data.get("threshold", 30)

    @property
    def is_on(self):
        device = self.coordinator.devices.get(self._address)
        if device is None:
            return False
        battery = device.get("battery")
        if battery is None:
            return False
        return battery <= self._threshold