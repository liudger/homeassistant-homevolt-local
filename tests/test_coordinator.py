"""Test the coordinator."""
import pytest
from unittest.mock import AsyncMock, Mock, patch
import aiohttp
import asyncio
from datetime import timedelta

from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.homevolt_local import (
    HomevoltDataUpdateCoordinator,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.homevolt_local.const import DOMAIN
from custom_components.homevolt_local.models import HomevoltData


class TestHomevoltDataUpdateCoordinator:
    """Test the HomevoltDataUpdateCoordinator."""

    def test_coordinator_init(self, mock_hass, mock_session):
        """Test coordinator initialization."""
        coordinator = HomevoltDataUpdateCoordinator(
            hass=mock_hass,
            logger=Mock(),
            entry_id="test_entry",
            resources=["http://192.168.1.100/ems.json"],
            hosts=["192.168.1.100"],
            main_host="192.168.1.100",
            username="test_user",
            password="test_pass",
            session=mock_session,
            update_interval=timedelta(seconds=30),
            timeout=30,
        )

        assert coordinator.entry_id == "test_entry"
        assert coordinator.resources == ["http://192.168.1.100/ems.json"]
        assert coordinator.hosts == ["192.168.1.100"]
        assert coordinator.main_host == "192.168.1.100"
        assert coordinator.username == "test_user"
        assert coordinator.password == "test_pass"
        assert coordinator.timeout == 30

    @pytest.mark.asyncio
    async def test_fetch_resource_data_success(self, mock_hass, mock_session, sample_homevolt_data):
        """Test successful resource data fetch."""
        # Mock the response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=sample_homevolt_data)
        
        mock_session.get = AsyncMock()
        mock_session.get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
        mock_session.get.return_value.__aexit__ = AsyncMock(return_value=None)

        coordinator = HomevoltDataUpdateCoordinator(
            hass=mock_hass,
            logger=Mock(),
            entry_id="test_entry",
            resources=["http://192.168.1.100/ems.json"],
            hosts=["192.168.1.100"],
            main_host="192.168.1.100",
            username="test_user",
            password="test_pass",
            session=mock_session,
            update_interval=timedelta(seconds=30),
            timeout=30,
        )

        result = await coordinator._fetch_resource_data("http://192.168.1.100/ems.json")
        assert result == sample_homevolt_data

    @pytest.mark.asyncio
    async def test_fetch_resource_data_http_error(self, mock_hass, mock_session):
        """Test resource data fetch with HTTP error."""
        # Mock the response with error status
        mock_response = AsyncMock()
        mock_response.status = 404
        
        mock_session.get = AsyncMock()
        mock_session.get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
        mock_session.get.return_value.__aexit__ = AsyncMock(return_value=None)

        coordinator = HomevoltDataUpdateCoordinator(
            hass=mock_hass,
            logger=Mock(),
            entry_id="test_entry",
            resources=["http://192.168.1.100/ems.json"],
            hosts=["192.168.1.100"],
            main_host="192.168.1.100",
            username="test_user",
            password="test_pass",
            session=mock_session,
            update_interval=timedelta(seconds=30),
            timeout=30,
        )

        with pytest.raises(UpdateFailed, match="Error communicating with API: 404"):
            await coordinator._fetch_resource_data("http://192.168.1.100/ems.json")

    @pytest.mark.asyncio
    async def test_fetch_resource_data_timeout(self, mock_hass, mock_session):
        """Test resource data fetch with timeout."""
        mock_session.get = AsyncMock(side_effect=asyncio.TimeoutError())

        coordinator = HomevoltDataUpdateCoordinator(
            hass=mock_hass,
            logger=Mock(),
            entry_id="test_entry",
            resources=["http://192.168.1.100/ems.json"],
            hosts=["192.168.1.100"],
            main_host="192.168.1.100",
            username="test_user",
            password="test_pass",
            session=mock_session,
            update_interval=timedelta(seconds=30),
            timeout=30,
        )

        with pytest.raises(UpdateFailed, match="Timeout error fetching data"):
            await coordinator._fetch_resource_data("http://192.168.1.100/ems.json")

    @pytest.mark.asyncio
    async def test_async_update_data_success(self, mock_hass, mock_session, sample_homevolt_data):
        """Test successful data update."""
        # Mock the response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=sample_homevolt_data)
        
        mock_session.get = AsyncMock()
        mock_session.get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
        mock_session.get.return_value.__aexit__ = AsyncMock(return_value=None)

        coordinator = HomevoltDataUpdateCoordinator(
            hass=mock_hass,
            logger=Mock(),
            entry_id="test_entry",
            resources=["http://192.168.1.100/ems.json"],
            hosts=["192.168.1.100"],
            main_host="192.168.1.100",
            username="test_user",
            password="test_pass",
            session=mock_session,
            update_interval=timedelta(seconds=30),
            timeout=30,
        )

        result = await coordinator._async_update_data()
        assert isinstance(result, HomevoltData)
        assert result.type == "homevolt_data"

    @pytest.mark.asyncio
    async def test_async_update_data_no_resources(self, mock_hass, mock_session):
        """Test data update with no resources."""
        coordinator = HomevoltDataUpdateCoordinator(
            hass=mock_hass,
            logger=Mock(),
            entry_id="test_entry",
            resources=[],
            hosts=[],
            main_host="",
            username="test_user",
            password="test_pass",
            session=mock_session,
            update_interval=timedelta(seconds=30),
            timeout=30,
        )

        with pytest.raises(UpdateFailed, match="No resources configured"):
            await coordinator._async_update_data()

    def test_merge_data_single_system(self, mock_hass, mock_session, sample_homevolt_data):
        """Test merging data from a single system."""
        coordinator = HomevoltDataUpdateCoordinator(
            hass=mock_hass,
            logger=Mock(),
            entry_id="test_entry",
            resources=["http://192.168.1.100/ems.json"],
            hosts=["192.168.1.100"],
            main_host="192.168.1.100",
            username="test_user",
            password="test_pass",
            session=mock_session,
            update_interval=timedelta(seconds=30),
            timeout=30,
        )

        results = [("192.168.1.100", sample_homevolt_data)]
        merged = coordinator._merge_data(results, sample_homevolt_data)

        assert merged["$type"] == "homevolt_data"
        assert len(merged["ems"]) == 1
        assert len(merged["sensors"]) == 1

    def test_merge_data_multiple_systems(self, mock_hass, mock_session, sample_homevolt_data):
        """Test merging data from multiple systems."""
        coordinator = HomevoltDataUpdateCoordinator(
            hass=mock_hass,
            logger=Mock(),
            entry_id="test_entry",
            resources=["http://192.168.1.100/ems.json", "http://192.168.1.101/ems.json"],
            hosts=["192.168.1.100", "192.168.1.101"],
            main_host="192.168.1.100",
            username="test_user",
            password="test_pass",
            session=mock_session,
            update_interval=timedelta(seconds=30),
            timeout=30,
        )

        # Create second system data with different IDs
        second_data = sample_homevolt_data.copy()
        second_data["ems"][0]["ecu_id"] = 2
        second_data["sensors"][0]["euid"] = "SENSOR004"

        results = [
            ("192.168.1.100", sample_homevolt_data),
            ("192.168.1.101", second_data)
        ]
        
        merged = coordinator._merge_data(results, sample_homevolt_data)

        # Should have 2 EMS systems and 2 sensors (1 from each system)
        assert len(merged["ems"]) == 2
        assert len(merged["sensors"]) == 2


class TestAsyncSetupEntry:
    """Test the async_setup_entry function."""

    @pytest.mark.asyncio
    async def test_setup_entry_single_resource(self, mock_hass, sample_config_data):
        """Test setting up entry with single resource (old format)."""
        mock_config_entry = Mock()
        mock_config_entry.data = sample_config_data
        mock_config_entry.entry_id = "test_entry"

        with patch("custom_components.homevolt_local.async_get_clientsession") as mock_get_session:
            mock_session = Mock()
            mock_get_session.return_value = mock_session
            
            with patch("custom_components.homevolt_local.HomevoltDataUpdateCoordinator") as mock_coordinator_class:
                mock_coordinator = Mock()
                mock_coordinator.async_config_entry_first_refresh = AsyncMock()
                mock_coordinator_class.return_value = mock_coordinator

                result = await async_setup_entry(mock_hass, mock_config_entry)

                assert result is True
                assert DOMAIN in mock_hass.data
                assert mock_config_entry.entry_id in mock_hass.data[DOMAIN]

    @pytest.mark.asyncio
    async def test_setup_entry_multiple_resources(self, mock_hass, sample_multi_config_data):
        """Test setting up entry with multiple resources (new format)."""
        mock_config_entry = Mock()
        mock_config_entry.data = sample_multi_config_data
        mock_config_entry.entry_id = "test_entry"

        with patch("custom_components.homevolt_local.async_get_clientsession") as mock_get_session:
            mock_session = Mock()
            mock_get_session.return_value = mock_session
            
            with patch("custom_components.homevolt_local.HomevoltDataUpdateCoordinator") as mock_coordinator_class:
                mock_coordinator = Mock()
                mock_coordinator.async_config_entry_first_refresh = AsyncMock()
                mock_coordinator_class.return_value = mock_coordinator

                result = await async_setup_entry(mock_hass, mock_config_entry)

                assert result is True
                assert DOMAIN in mock_hass.data
                assert mock_config_entry.entry_id in mock_hass.data[DOMAIN]


class TestAsyncUnloadEntry:
    """Test the async_unload_entry function."""

    @pytest.mark.asyncio
    async def test_unload_entry_success(self, mock_hass):
        """Test successful entry unload."""
        mock_config_entry = Mock()
        mock_config_entry.entry_id = "test_entry"
        
        # Setup initial state
        mock_hass.data[DOMAIN] = {"test_entry": Mock()}

        result = await async_unload_entry(mock_hass, mock_config_entry)

        assert result is True
        assert "test_entry" not in mock_hass.data[DOMAIN]

    @pytest.mark.asyncio
    async def test_unload_entry_failure(self, mock_hass):
        """Test entry unload failure."""
        mock_config_entry = Mock()
        mock_config_entry.entry_id = "test_entry"
        
        # Setup initial state
        mock_hass.data[DOMAIN] = {"test_entry": Mock()}
        
        # Make unload fail
        mock_hass.config_entries.async_unload_platforms = AsyncMock(return_value=False)

        result = await async_unload_entry(mock_hass, mock_config_entry)

        assert result is False
        # Entry should still be in data since unload failed
        assert "test_entry" in mock_hass.data[DOMAIN]