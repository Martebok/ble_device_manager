import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.components.bluetooth import async_ble_device_from_address, async_last_service_info
from bleak import BleakClient
from bleak.exc import BleakError

_LOGGER = logging.getLogger(__name__)

BATTERY_UUID = "00002a19-0000-1000-8000-00805f9b34fb"
CONNECT_TIMEOUT = 10.0
READ_TIMEOUT = 5.0

class BLEDeviceCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry):
        self.address = entry.data["address"]
        self.device_name = entry.data["name"]
        self.charge_threshold = entry.data.get("charge_threshold", 30)
        self.is_ignored = entry.data.get("is_ignored", False)
        
        super().__init__(
            hass,
            _LOGGER,
            name=self.device_name,
            update_interval=timedelta(seconds=300),
        )

    async def _async_update_data(self):
        if self.is_ignored:
            return {"present": False, "battery": None}

        service_info = async_last_service_info(self.hass, self.address, connectable=True)
        is_present = service_info is not None

        battery_level = None

        if is_present:
            ble_device = async_ble_device_from_address(self.hass, self.address, connectable=True)
            if ble_device:
                try:
                    battery_level = await self._read_battery(ble_device)
                except BleakError as err:
                    _LOGGER.debug("Dispositivo %s occupato o non raggiungibile per GATT: %s", self.device_name, err)
                except Exception as err:
                    _LOGGER.warning("Errore imprevisto lettura batteria %s: %s", self.device_name, err)

        return {
            "present": is_present,
            "battery": battery_level,
        }

    async def _read_battery(self, ble_device):
        client = BleakClient(ble_device, timeout=CONNECT_TIMEOUT)
        try:
            await client.connect()
            if not client.is_connected:
                return None
            
            value = await client.read_gatt_char(BATTERY_UUID)
            return int(value[0]) if value else None
        finally:
            if client.is_connected:
                await client.disconnect()