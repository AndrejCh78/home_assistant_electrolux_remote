"""Base switch class"""

import logging
from typing import Optional

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.switch import SwitchEntity
from ..update_coordinator import Coordinator

_LOGGER = logging.getLogger(__name__)


class SwitchDevice(CoordinatorEntity, SwitchEntity):
    def __init__(
        self,
        uid: str,
        name: str,
        coordinator: Coordinator,
        icon,
        device,
        param_name: str,
        property_name: str,
        value_on,
        value_off
    ):
        """
        Initialize
        """
        self.coordinator = coordinator

        super().__init__(coordinator)

        self._uid = uid
        self._name = name
        self._icon = icon
        self._device = device
        self._param_name = param_name
        self._property_name = property_name
        self._value_off = value_off
        self._value_on = value_on

        coordinator.async_add_listener(self._update)
        self._update()

    @property
    def name(self):
        """Return the name."""
        return self._name

    @property
    def icon(self) -> Optional[str]:
        """Return the icon to use in the frontend, if any."""
        return self._icon

    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on."""
        return getattr(self._device, self._property_name)

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        if getattr(self._device, self._property_name):
            return

        params = {self._param_name: self._value_on}

        result = await self.coordinator.api.set_device_params(self._uid, params)

        if result:
            self._update_coordinator_data(params)

    async def async_turn_off(self) -> None:
        """Turn the entity off."""
        if not getattr(self._device, self._property_name):
            return

        params = {self._param_name: self._value_off}

        result = await self.coordinator.api.set_device_params(self._uid, params)

        if result:
            self._update_coordinator_data(params)

    def _update(self) -> None:
        """
        Update local data
        """
        for data in self.coordinator.data:
            if data["uid"] == self._uid:
                self._device.from_json(data)

    def _update_coordinator_data(self, params: dict) -> None:
        """Update data in coordinator"""
        devices = self.coordinator.data

        for index, device in enumerate(devices):
            if device["uid"] == self._uid:
                for param in params:
                    devices[index][param] = params[param]

        self.coordinator.async_set_updated_data(devices)
        self._update()
