import asyncio
import logging
from datetime import timedelta

from bleak import BleakClient, BleakError
from homeassistant.components.bluetooth import (
    async_discovered_service_info,
    async_last_service_info,
)
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)

# Caratteristica GATT standard per livello batteria (%)
BATTERY_CHARACTERISTIC = "00002a19-0000-1000-8000-00805f9b34fb"


class BLEGlobalCoordinator(DataUpdateCoordinator):
    """Coordinator condiviso: traccia tutti i dispositivi BLE registrati."""

    def __init__(self, hass):
        self.hass = hass
        # address -> {"name", "threshold", "present", "battery", "last_seen"}
        self.devices = {}
        self._lock = asyncio.Lock()

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def async_register_device(self, address, name, threshold):
        """Aggiunge un dispositivo al coordinator (chiamato da async_setup_entry)."""
        async with self._lock:
            self.devices[address] = {
                "name": name,
                "threshold": threshold,
                "present": False,
                "battery": None,
                "last_seen": None,
            }
        self.async_set_updated_data(self.devices)

    async def async_unregister_device(self, address):
        """Rimuove un dispositivo dal coordinator (chiamato da async_unload_entry)."""
        async with self._lock:
            self.devices.pop(address, None)
        self.async_set_updated_data(self.devices)

    async def _async_update_data(self):
        """Ogni ciclo: controlla presenza e legge la batteria per i dispositivi presenti."""
        discovered = async_discovered_service_info(self.hass)
        discovered_addresses = {d.address for d in discovered}

        for address, device in list(self.devices.items()):
            service_info = async_last_service_info(self.hass, address)
            present = service_info is not None
            device["present"] = present
            if present:
                device["last_seen"] = self.hass.loop.time()

            if not present:
                continue

            # Il dispositivo è presente: prova a leggere la batteria.
            # Se è già occupo da un'altra connessione (TV/phone), BleakError viene
            # catturato silenziosamente e si riprova al ciclo successivo.
            try:
                async with BleakClient(
                    address,
                    timeout=10,
                    pair=False,
                ) as client:
                    raw = await client.read_gatt_char(BATTERY_CHARACTERISTIC)
                    if isinstance(raw, (bytes, bytearray)):
                        device["battery"] = int.from_bytes(raw, "little")
                    else:
                        device["battery"] = int(raw)
            except (BleakError, asyncio.TimeoutError) as err:
                _LOGGER.debug(
                    "Impossibile leggere batteria per %s (%s): %s",
                    device["name"], address, err,
                )

        return self.devices