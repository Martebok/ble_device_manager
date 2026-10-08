import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_ADDRESS, CONF_NAME
from homeassistant.components.bluetooth import async_discovered_service_info
from .const import DOMAIN

class BLEDeviceManagerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def _get_discovered_devices(self):
        """Get list of discovered Bluetooth devices from HA."""
        devices = {}
        for service_info in async_discovered_service_info(self.hass):
            address = service_info.address
            name = service_info.name or f"Unknown ({address})"
            if address not in devices:
                devices[address] = f"{name} ({address})"
        return devices

    async def async_step_user(self, user_input=None):
        errors = {}
        discovered = self._get_discovered_devices()
        
        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            # If user selected from dropdown, extract MAC from "Name (MAC)"
            if " (" in address and address.endswith(")"):
                address = address.split(" (")[-1][:-1]
            user_input[CONF_ADDRESS] = address
            return self.async_create_entry(
                title=user_input.get(CONF_NAME, "BLE Device"),
                data=user_input
            )

        # Build schema with device selector
        address_options = list(discovered.values())
        address_options.append("--- Inserisci manualmente ---")
        
        data_schema = vol.Schema({
            vol.Required(CONF_NAME, default="P47 Rosso"): str,
            vol.Required(CONF_ADDRESS): vol.In(address_options),
            vol.Optional("is_ignored", default=False): bool,
            vol.Optional("charge_threshold", default=30): int,
        })

        return self.async_show_form(
            step_id="user", 
            data_schema=data_schema, 
            errors=errors,
            description_placeholders={
                "discovered_count": str(len(discovered))
            }
        )