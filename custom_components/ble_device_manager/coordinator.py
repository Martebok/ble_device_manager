import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.components.bluetooth import async_discovered_service_info, async_ble_device_from_address

_LOGGER = logging.getLogger(__name__)

class BLEGlobalCoordinator(DataUpdateCoordinator):
    def __init__(self, hass):
        self.hass = hass
        # Liste in memoria per tracciare cosa è monitorato e cosa è ignorato
        self.monitored = {}  # Esempio: {"AA:BB:CC:...": {"name": "P47 Rosso", "threshold": 30}}
        self.ignored = set() # Esempio: {"11:22:33:..."}
        
        super().__init__(
            hass,
            _LOGGER,
            name="BLE Global Radar",
            update_interval=timedelta(seconds=60), # Scansione radar ogni minuto
        )

    async def _async_update_data(self):
        # 1. Rileva tutti i dispositivi attualmente nell'etere
        discovered = async_discovered_service_info(self.hass)
        devices_data = {}

        for d in discovered:
            address = d.address
            name = d.name or "Sconosciuto"
            rssi = d.rssi

            if address in self.ignored:
                status = "ignored"
            elif address in self.monitored:
                status = "monitored"
                # Qui esegue il controllo GATT con timer 5 min se libero
            else:
                status = "discovering" # Nuovo dispositivo trovato nell'etere

            devices_data[address] = {
                "name": name,
                "address": address,
                "rssi": rssi,
                "status": status,
                "present": True,
                "battery": None # Sarà aggiornato via GATT se monitorato
            }

        return devices_data

    def add_monitored(self, address, name, threshold=30):
        if address in self.ignored:
            self.ignored.remove(address)
        self.monitored[address] = {"name": name, "threshold": threshold}
        self.async_set_updated_data(self.data)

    def add_ignored(self, address):
        if address in self.monitored:
            del self.monitored[address]
        self.ignored.add(address)
        self.async_set_updated_data(self.data)
