# BLE Device Manager

Custom Home Assistant integration for managing BLE devices with passive presence detection and smart battery polling.

**Repository:** https://github.com/Martebok/ble_device_manager

## Features

- **Passive presence detection** - Uses Bluetooth advertising packets (RSSI) to detect device presence without connecting
- **Smart GATT polling** - Reads battery level (0x2A19) every 5+ minutes only when device is present and not busy
- **Conflict avoidance** - Gracefully handles devices occupied by other connections (TV, smartphone)
- **Custom labels** - Friendly names like "P47 Rosso" for each device
- **Ignored devices list** - Separate tab for devices you don't want to monitor
- **Binary sensors** - Presence (green/gray dot) + "Needs Charge" boolean for automations
- **HACS compatible** - Ready for Home Assistant Community Store

## Installation

### Manual (Local)

1. Copy `custom_components/ble_device_manager` to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant
3. Go to **Settings > Devices & Services > Add Integration** > Search "BLE Device Manager"

### HACS (Future)

Once published, will be available via HACS > Integrations > Explore & Add > "BLE Device Manager"

## Configuration

1. Add integration via UI
2. Enter device **Name** (e.g., "P47 Rosso"), **MAC Address**
3. Optional: Set **Charge Threshold** (default 30%) and **Ignore** toggle
4. Repeat for each device

## Entities Created Per Device

| Entity | Type | Description |
|--------|------|-------------|
| `sensor.{name}_batteria` | Sensor | Battery percentage (0-100%) |
| `binary_sensor.{name}_presenza` | Binary Sensor | Presence detection (connectivity) |
| `binary_sensor.{name}_da_ricaricare` | Binary Sensor | True when battery ≤ threshold |

## Architecture

```
custom_components/ble_device_manager/
├── __init__.py          # Entry setup/teardown
├── manifest.json        # Integration metadata + bleak dependency
├── const.py             # Constants
├── config_flow.py       # UI configuration flow
├── coordinator.py       # Passive RSSI + GATT polling (5min interval)
├── sensor.py            # Battery sensor entity
└── binary_sensor.py     # Presence + Needs Charge binary sensors
```

## Requirements

- Home Assistant 2024.6+
- Bluetooth integration enabled
- `bleak>=0.22.0` (auto-installed via manifest)

## How It Works

1. **Passive scan** - HA's Bluetooth integration captures advertising packets continuously
2. **Presence check** - Every 5 min, coordinator checks `async_last_service_info()` for recent advertisement
3. **Battery read** - If present, attempts quick GATT connection to read 0x2A19 characteristic
4. **Conflict handling** - If device is busy (connected to TV/phone), `BleakError` caught silently, retry next cycle
5. **Clean disconnect** - Client always disconnected after read to free device

## License

MIT License - see [LICENSE](LICENSE)