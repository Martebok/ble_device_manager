import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_ADDRESS, CONF_NAME
from .const import DOMAIN

class BLEDeviceManagerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(
                title=user_input.get(CONF_NAME, "BLE Device"),
                data=user_input
            )

        data_schema = vol.Schema({
            vol.Required(CONF_NAME, default="P47 Rosso"): str,
            vol.Required(CONF_ADDRESS): str,
            vol.Optional("is_ignored", default=False): bool,
            vol.Optional("charge_threshold", default=30): int,
        })

        return self.async_show_form(
            step_id="user", 
            data_schema=data_schema, 
            errors=errors
        )