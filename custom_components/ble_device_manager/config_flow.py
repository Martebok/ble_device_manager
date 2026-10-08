import asyncio
import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components.bluetooth import async_discovered_service_info
from homeassistant.core import callback

from .const import (
    CONF_ADDRESS,
    CONF_IGNORE,
    CONF_NAME,
    CONF_THRESHOLD,
    DEFAULT_BATTERY_THRESHOLD,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class BLEDeviceManagerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self._discovered = {}  # address -> name
        self._selected_address = None

    async def async_step_user(self, user_input=None):
        """Primo passo: seleziona un dispositivo dall'etere o inseriscilo manualmente."""
        # Rileva i dispositivi attualmente nell'etere
        self._discovered = {}
        try:
            service_infos = async_discovered_service_info(self.hass)
            for info in service_infos:
                name = info.name or info.address
                self._discovered[info.address] = name
        except Exception as err:  # pragma: no cover - dipende dall'adapter
            _LOGGER.debug("Impossibile leggere i dispositivi dall'etere: %s", err)

        if user_input is not None:
            choice = user_input.get("device")
            if choice == "__manual__":
                return await self.async_step_manual()
            self._selected_address = choice
            return await self.async_step_details()

        # Costruisci il dropdown: dispositivi scoperti + opzione manuale
        device_choices = {addr: f"{name} ({addr})" for addr, name in self._discovered.items()}
        device_choices["__manual__"] = "Inserisci indirizzo manualmente"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("device"): vol.In(device_choices),
            }),
            description_placeholders={
                "count": str(len(self._discovered)),
            },
        )

    async def async_step_manual(self, user_input=None):
        """Passo per l'inserimento manuale del MAC."""
        if user_input is not None:
            self._selected_address = user_input["address"]
            return await self.async_step_details(user_input={"name": user_input["name"]})

        return self.async_show_form(
            step_id="manual",
            data_schema=vol.Schema({
                vol.Required("name"): str,
                vol.Required("address"): str,
            }),
        )

    async def async_step_details(self, user_input=None):
        """Secondo passo: nome, soglia e toggle ignore."""
        address = self._selected_address
        default_name = self._discovered.get(address, address)

        if user_input is not None:
            return self.async_create_entry(
                title=user_input["name"],
                data={
                    CONF_NAME: user_input["name"],
                    CONF_ADDRESS: address,
                    CONF_THRESHOLD: user_input.get(CONF_THRESHOLD, DEFAULT_BATTERY_THRESHOLD),
                    CONF_IGNORE: user_input.get(CONF_IGNORE, False),
                },
            )

        return self.async_show_form(
            step_id="details",
            data_schema=vol.Schema({
                vol.Required("name", default=default_name): str,
                vol.Optional(CONF_THRESHOLD, default=DEFAULT_BATTERY_THRESHOLD): vol.Coerce(int),
                vol.Optional(CONF_IGNORE, default=False): bool,
            }),
        )