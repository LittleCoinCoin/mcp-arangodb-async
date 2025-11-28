"""Unit tests for multi-tenancy MCP tools."""

import pytest
from unittest.mock import Mock, AsyncMock
from mcp_arangodb_async.handlers import (
    handle_set_focused_database,
    handle_get_focused_database,
    handle_list_available_databases,
    handle_get_database_resolution,
    handle_test_database_connection,
    handle_get_multi_database_status,
)
from mcp_arangodb_async.session_state import SessionState
from mcp_arangodb_async.multi_db_manager import MultiDatabaseConnectionManager
from mcp_arangodb_async.config_loader import ConfigFileLoader, DatabaseConfig


class TestMultiTenancyTools:
    """Test multi-tenancy MCP tools."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_db = Mock()
        self.session_state = SessionState()
        self.session_id = "test_session"
        self.session_state.initialize_session(self.session_id)
        
        # Create mock db_manager
        self.db_manager = Mock(spec=MultiDatabaseConnectionManager)
        self.db_manager.get_configured_databases.return_value = {
            "production": DatabaseConfig(
                url="http://localhost:8529",
                database="prod_db",
                username="admin",
                password_env="ARANGO_PROD_PASSWORD",
                timeout=30
            ),
            "staging": DatabaseConfig(
                url="http://localhost:8530",
                database="staging_db",
                username="admin",
                password_env="ARANGO_STAGING_PASSWORD",
                timeout=30
            )
        }
        
        # Create mock config_loader
        self.config_loader = Mock(spec=ConfigFileLoader)
        self.config_loader.default_database = "production"
        self.config_loader.get_configured_databases.return_value = self.db_manager.get_configured_databases()

    def _create_session_context(self):
        """Create session context for handlers."""
        return {
            "_session_context": {
                "session_state": self.session_state,
                "session_id": self.session_id,
                "db_manager": self.db_manager,
                "config_loader": self.config_loader
            }
        }

    @pytest.mark.asyncio
    async def test_set_focused_database_success(self):
        """Test setting focused database successfully."""
        args = {
            "database": "staging",
            **self._create_session_context()
        }
        
        result = await handle_set_focused_database(self.mock_db, args)
        
        assert result["success"] is True
        assert result["focused_database"] == "staging"
        assert result["session_id"] == self.session_id
        assert self.session_state.get_focused_database(self.session_id) == "staging"

    @pytest.mark.asyncio
    async def test_set_focused_database_invalid(self):
        """Test setting focused database with invalid database key."""
        args = {
            "database": "nonexistent",
            **self._create_session_context()
        }
        
        result = await handle_set_focused_database(self.mock_db, args)
        
        assert result["success"] is False
        assert "not configured" in result["error"]
        assert "available_databases" in result

    @pytest.mark.asyncio
    async def test_set_focused_database_no_session_state(self):
        """Test setting focused database without session state."""
        args = {
            "database": "production",
            "_session_context": {
                "session_state": None,
                "session_id": self.session_id,
                "db_manager": self.db_manager,
                "config_loader": self.config_loader
            }
        }
        
        result = await handle_set_focused_database(self.mock_db, args)
        
        assert result["success"] is False
        assert "Session state not available" in result["error"]

    def test_get_focused_database_set(self):
        """Test getting focused database when it's set."""
        import asyncio
        asyncio.run(self.session_state.set_focused_database(self.session_id, "production"))
        
        args = self._create_session_context()
        result = handle_get_focused_database(self.mock_db, args)
        
        assert result["focused_database"] == "production"
        assert result["session_id"] == self.session_id
        assert result["is_set"] is True

    def test_get_focused_database_not_set(self):
        """Test getting focused database when it's not set."""
        args = self._create_session_context()
        result = handle_get_focused_database(self.mock_db, args)
        
        assert result["focused_database"] is None
        assert result["session_id"] == self.session_id
        assert result["is_set"] is False

    def test_get_focused_database_no_session_state(self):
        """Test getting focused database without session state."""
        args = {
            "_session_context": {
                "session_state": None,
                "session_id": self.session_id,
                "db_manager": self.db_manager,
                "config_loader": self.config_loader
            }
        }
        
        result = handle_get_focused_database(self.mock_db, args)

        assert result["focused_database"] is None
        assert result["is_set"] is False
        assert "Session state not available" in result["error"]

    def test_list_available_databases(self):
        """Test listing available databases."""
        args = self._create_session_context()
        result = handle_list_available_databases(self.mock_db, args)

        assert result["total_count"] == 2
        assert len(result["databases"]) == 2

        # Check database details
        db_keys = [db["key"] for db in result["databases"]]
        assert "production" in db_keys
        assert "staging" in db_keys

        # Check production database details
        prod_db = next(db for db in result["databases"] if db["key"] == "production")
        assert prod_db["url"] == "http://localhost:8529"
        assert prod_db["database"] == "prod_db"
        assert prod_db["username"] == "admin"

    def test_list_available_databases_no_db_manager(self):
        """Test listing available databases without db_manager."""
        args = {
            "_session_context": {
                "session_state": self.session_state,
                "session_id": self.session_id,
                "db_manager": None,
                "config_loader": self.config_loader
            }
        }

        result = handle_list_available_databases(self.mock_db, args)

        assert result["total_count"] == 0
        assert result["databases"] == []
        assert "Database manager not available" in result["error"]

    def test_get_database_resolution(self):
        """Test database resolution display."""
        import asyncio
        asyncio.run(self.session_state.set_focused_database(self.session_id, "staging"))

        args = self._create_session_context()
        result = handle_get_database_resolution(self.mock_db, args)

        assert result["session_id"] == self.session_id
        assert result["resolved_database"] == "staging"
        assert result["resolved_level"] == "2_focused_database"

        # Check all levels
        assert result["levels"]["1_per_tool_override"]["value"] is None
        assert result["levels"]["2_focused_database"]["value"] == "staging"
        assert result["levels"]["3_config_default"]["value"] == "production"
        assert result["levels"]["5_first_configured"]["value"] == "production"
        assert result["levels"]["6_hardcoded_fallback"]["value"] == "_system"

    def test_get_database_resolution_no_focused(self):
        """Test database resolution when no focused database is set."""
        args = self._create_session_context()
        result = handle_get_database_resolution(self.mock_db, args)

        assert result["session_id"] == self.session_id
        assert result["resolved_database"] == "production"
        assert result["resolved_level"] == "3_config_default"

    def test_get_database_resolution_fallback_to_first_configured(self):
        """Test database resolution falls back to first configured database."""
        self.config_loader.default_database = None

        args = self._create_session_context()
        result = handle_get_database_resolution(self.mock_db, args)

        assert result["resolved_database"] == "production"
        assert result["resolved_level"] == "5_first_configured"

    @pytest.mark.asyncio
    async def test_test_database_connection_success(self):
        """Test database connection test successfully."""
        # Mock successful connection
        mock_client = Mock()
        mock_test_db = Mock()
        mock_test_db.version.return_value = "3.11.0"
        self.db_manager.get_connection = AsyncMock(return_value=(mock_client, mock_test_db))

        args = {
            "database": "production",
            **self._create_session_context()
        }

        result = await handle_test_database_connection(self.mock_db, args)

        assert result["success"] is True
        assert result["database"] == "production"
        assert result["version"] == "3.11.0"
        assert result["url"] == "http://localhost:8529"
        assert result["database_name"] == "prod_db"

    @pytest.mark.asyncio
    async def test_test_database_connection_failure(self):
        """Test database connection test with connection failure."""
        # Mock connection failure
        self.db_manager.get_connection = AsyncMock(side_effect=Exception("Connection refused"))

        args = {
            "database": "production",
            **self._create_session_context()
        }

        result = await handle_test_database_connection(self.mock_db, args)

        assert result["success"] is False
        assert result["database"] == "production"
        assert "Connection refused" in result["error"]

    @pytest.mark.asyncio
    async def test_test_database_connection_invalid_database(self):
        """Test database connection test with invalid database key."""
        args = {
            "database": "nonexistent",
            **self._create_session_context()
        }

        result = await handle_test_database_connection(self.mock_db, args)

        assert result["success"] is False
        assert "not configured" in result["error"]
        assert "available_databases" in result

    @pytest.mark.asyncio
    async def test_test_database_connection_no_db_manager(self):
        """Test database connection test without db_manager."""
        args = {
            "database": "production",
            "_session_context": {
                "session_state": self.session_state,
                "session_id": self.session_id,
                "db_manager": None,
                "config_loader": self.config_loader
            }
        }

        result = await handle_test_database_connection(self.mock_db, args)

        assert result["success"] is False
        assert "Database manager not available" in result["error"]

    @pytest.mark.asyncio
    async def test_get_multi_database_status_all_connected(self):
        """Test getting status of all databases when all are connected."""
        await self.session_state.set_focused_database(self.session_id, "production")

        # Mock successful connections for both databases
        async def mock_get_connection(db_key):
            mock_client = Mock()
            mock_test_db = Mock()
            if db_key == "production":
                mock_test_db.version.return_value = "3.11.0"
            else:
                mock_test_db.version.return_value = "3.10.5"
            return mock_client, mock_test_db

        self.db_manager.get_connection = mock_get_connection

        args = self._create_session_context()
        result = await handle_get_multi_database_status(self.mock_db, args)

        assert result["total_count"] == 2
        assert result["focused_database"] == "production"
        assert result["session_id"] == self.session_id
        assert len(result["databases"]) == 2

        # Check production database status
        prod_db = next(db for db in result["databases"] if db["key"] == "production")
        assert prod_db["status"] == "connected"
        assert prod_db["version"] == "3.11.0"
        assert prod_db["is_focused"] is True

        # Check staging database status
        staging_db = next(db for db in result["databases"] if db["key"] == "staging")
        assert staging_db["status"] == "connected"
        assert staging_db["version"] == "3.10.5"
        assert staging_db["is_focused"] is False

    @pytest.mark.asyncio
    async def test_get_multi_database_status_mixed_connectivity(self):
        """Test getting status when some databases fail to connect."""
        # Mock mixed connectivity
        async def mock_get_connection(db_key):
            if db_key == "production":
                mock_client = Mock()
                mock_test_db = Mock()
                mock_test_db.version.return_value = "3.11.0"
                return mock_client, mock_test_db
            else:
                raise Exception("Connection timeout")

        self.db_manager.get_connection = mock_get_connection

        args = self._create_session_context()
        result = await handle_get_multi_database_status(self.mock_db, args)

        assert result["total_count"] == 2

        # Check production database status (connected)
        prod_db = next(db for db in result["databases"] if db["key"] == "production")
        assert prod_db["status"] == "connected"
        assert prod_db["version"] == "3.11.0"

        # Check staging database status (error)
        staging_db = next(db for db in result["databases"] if db["key"] == "staging")
        assert staging_db["status"] == "error"
        assert "Connection timeout" in staging_db["error"]

    @pytest.mark.asyncio
    async def test_get_multi_database_status_no_db_manager(self):
        """Test getting multi-database status without db_manager."""
        args = {
            "_session_context": {
                "session_state": self.session_state,
                "session_id": self.session_id,
                "db_manager": None,
                "config_loader": self.config_loader
            }
        }

        result = await handle_get_multi_database_status(self.mock_db, args)

        assert result["total_count"] == 0
        assert result["databases"] == []
        assert "Database manager not available" in result["error"]

    @pytest.mark.asyncio
    async def test_get_multi_database_status_no_focused_database(self):
        """Test getting multi-database status when no database is focused."""
        # Mock successful connections
        async def mock_get_connection(db_key):
            mock_client = Mock()
            mock_test_db = Mock()
            mock_test_db.version.return_value = "3.11.0"
            return mock_client, mock_test_db

        self.db_manager.get_connection = mock_get_connection

        args = self._create_session_context()
        result = await handle_get_multi_database_status(self.mock_db, args)

        assert result["focused_database"] is None
        assert all(not db["is_focused"] for db in result["databases"])

