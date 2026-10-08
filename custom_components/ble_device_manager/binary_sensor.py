from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    if not coordinator.is_ignored:
        async_add_entities([
            BLEPresenceSensor(coordinator, entry),
            BLENeedsChargeSensor(coordinator, entry)
        ])

class BLEPresenceSensor(CoordinatorEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_name = f"{entry.data['name']} Presenza"
        self._attr_unique_id = f"{entry.data['address']}_presence"

    @property
    def is_on(self):
        if self.coordinator.data:
            return self.coordinator.data.get("present", False)
        return False

class BLENeedsChargeSensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_name = f"{entry.data['name']} Da Ricaricare"
        self._attr_unique_id = f"{entry.data['address']}_needs_charge"
        self.threshold = coordinator.charge_threshold

    @property
    def is_on(self):
        data = self.coordinator.data
        if data and data.get("battery") is not None:
            return data.get("battery") <= self.threshold
        return False