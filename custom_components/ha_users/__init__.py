"""The Home Assistant Users integration."""
from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers import discovery
from homeassistant.helpers.typing import ConfigType
from homeassistant.const import Platform

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Home Assistant Users component from yaml."""
    _LOGGER.info("Setting up Home Assistant Users integration")
    
    # Store empty dict for this domain
    hass.data.setdefault(DOMAIN, {})
    
    # Check if our integration is configured
    if DOMAIN not in config:
        return True
    
    # Forward to platform setup
    await discovery.async_load_platform(hass, Platform.SENSOR, DOMAIN, {}, config)
    
    return True