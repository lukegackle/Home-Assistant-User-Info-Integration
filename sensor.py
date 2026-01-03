"""Support for Home Assistant user sensors."""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN, SCAN_INTERVAL_HOURS

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up Home Assistant user sensors from yaml config."""
    _LOGGER.info("Setting up HA Users sensors")
    
    try:
        coordinator = UserCoordinator(hass)
        # Use async_refresh instead of async_config_entry_first_refresh for YAML setup
        await coordinator.async_refresh()
        
        # Store coordinator
        hass.data[DOMAIN]["coordinator"] = coordinator
        
        # Create sensors for each user
        entities = []
        for user in coordinator.data:
            entities.append(UserSensor(coordinator, user))
        
        _LOGGER.info(f"Created {len(entities)} user sensors")
        
        # Add entities with update_before_add=False to prevent overriding entity_id
        async_add_entities(entities, update_before_add=False)
    except Exception as err:
        _LOGGER.error(f"Error setting up HA Users sensors: {err}", exc_info=True)
        raise


class UserCoordinator(DataUpdateCoordinator):
    """Coordinator to manage user data updates."""
    
    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=SCAN_INTERVAL_HOURS),
        )
    
    async def _async_update_data(self) -> list[dict]:
        """Fetch user data from Home Assistant auth system."""
        _LOGGER.debug("Fetching users from Home Assistant")
        
        # Access the auth store directly
        auth_store = self.hass.auth
        users = await auth_store.async_get_users()
        
        # Convert User objects to dicts
        user_list = []
        for user in users:
            user_dict = {
                'id': user.id,
                'name': user.name,
                'is_owner': user.is_owner,
                'is_active': user.is_active,
                'system_generated': user.system_generated,
                'group_ids': [g.id for g in user.groups],
            }
            
            # Add local_only if it exists (might not be in all HA versions)
            if hasattr(user, 'local_only'):
                user_dict['local_only'] = user.local_only
            else:
                user_dict['local_only'] = False
            
            # Check for credentials
            user_dict['has_credentials'] = len(user.credentials) > 0 if hasattr(user, 'credentials') else False
            
            user_list.append(user_dict)
        
        _LOGGER.debug(f"Found {len(user_list)} users")
        return user_list


class UserSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Home Assistant user sensor."""
    
    def __init__(self, coordinator: UserCoordinator, user: dict) -> None:
        """Initialize the user sensor."""
        super().__init__(coordinator)
        self._user_id = user['id']
        
        # Set up entity naming - use username or name
        username = user['name'] or f"user_{user['id'][:8]}"
        safe_name = username.lower().replace(' ', '_')
        
        # CRITICAL: Set unique_id with ha_user prefix
        self._attr_unique_id = f"ha_user_{safe_name}"
        
        # Set object_id which determines the entity_id suffix
        self._attr_object_id = f"ha_user_{safe_name}"
        
        # Set the name
        self._attr_name = f"ha_user_{safe_name}"
        
        self._update_from_user(user)
    
    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        user = self._find_user()
        if user:
            self._update_from_user(user)
        self.async_write_ha_state()
    
    def _find_user(self) -> dict | None:
        """Find this sensor's user in the coordinator data."""
        for user in self.coordinator.data:
            if user['id'] == self._user_id:
                return user
        return None
    
    def _update_from_user(self, user: dict) -> None:
        """Update sensor attributes from user dict."""
        friendly_name = user['name'] or f"User {user['id'][:8]}"
        self._attr_native_value = friendly_name
        
        self._attr_extra_state_attributes = {
            "user_id": user['id'],
            "is_owner": user['is_owner'],
            "is_active": user['is_active'],
            "local_only": user.get('local_only', False),
            "system_generated": user['system_generated'],
            "group_ids": user['group_ids'],
            "has_credentials": user.get('has_credentials', False),
        }