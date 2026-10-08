import asyncio
import logging

from bleak import BleakError, BleakScanner

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)


class LocalBLEGlobalCoordinator:
    """Simulatore locale del coordinatore di Home Assistant."""

    def __init__(self):
        # Dizionari di simulazione per testare la logica
        self.monitored = {
            "9C:8C:6E:DF:7F:A9": {"name": "TV Samsung Living", "threshold": 30}
        }
        self.ignored = {
            "7D:9D:54:57:17:B6"
        }

    async def async_update_data(self):
        print("[SCAN] Scansione dell'etere in corso (5 secondi)...")
        devices_data = {}

        try:
            async with BleakScanner() as scanner:
                discovered = await scanner.discover(timeout=5.0)
        except BleakError as err:
            _LOGGER.error("Errore durante la scansione BLE: %s", err)
            return devices_data

        for d in discovered:
            address = d.address
            name = d.name or "Sconosciuto"
            rssi = getattr(d, "rssi", None)

            # Logica di smistamento dello stato
            if address in self.ignored:
                status = "[IGNORED] Ignorato"
            elif address in self.monitored:
                status = "[MONITORATO] Monitorato"
            else:
                status = "[NUEVO] Nuovo / Non censito"

            devices_data[address] = {
                "name": name,
                "address": address,
                "rssi": rssi,
                "status": status,
            }

        return devices_data

    def add_monitored(self, address: str, name: str):
        self.ignored.discard(address)
        self.monitored[address] = {"name": name, "threshold": 30}
        print(f"\n[AZIONATA] Aggiunto ai monitorati: {address} -> {name}")

    def add_ignored(self, address: str):
        self.monitored.pop(address, None)
        self.ignored.add(address)
        print(f"\n[AZIONATA] Spostato negli ignorati: {address}")


async def main():
    coordinator = LocalBLEGlobalCoordinator()

    # 1. Prima scansione
    results = await coordinator.async_update_data()

    print(f"\n[OK] Trovati {len(results)} dispositivi:\n")
    print(f"{'MAC ADDRESS':<20} | {'NOME':<25} | {'RSSI':<8} | {'STATO'}")
    print("-" * 70)
    for mac, info in results.items():
        rssi_str = f"{info['rssi']} dBm" if info['rssi'] is not None else "N/D"
        print(f"{mac:<20} | {info['name'][:25]:<25} | {rssi_str:<8} | {info['status']}")

    # 2. Test interazione (Simulazione azioni dei pulsanti)
    if results:
        sample_mac = list(results.keys())[0]
        print(f"\n--- SIMULAZIONE AZIONE UTENTE ---")
        coordinator.add_monitored(sample_mac, "Dispositivo di Test")

        # 3. Seconda scansione per verificare l'aggiornamento dello stato
        print("\n--- SECONDA SCANSIONE (Post-Modifica) ---")
        updated_results = await coordinator.async_update_data()
        if sample_mac in updated_results:
            print(f"Stato aggiornato per {sample_mac}: {updated_results[sample_mac]['status']}")
        else:
            print(f"Dispositivo {sample_mac} non più nell'etere")


if __name__ == "__main__":
    asyncio.run(main())