"""Unit tests for CLI database management tool."""

import pytest
import os
import tempfile
import yaml
from unittest.mock import patch, Mock, AsyncMock
from argparse import Namespace
from mcp_arangodb_async.cli_db import (
    handle_add,
    handle_remove,
    handle_list,
    handle_test,
    handle_status,
)
from mcp_arangodb_async.multi_db_manager import DatabaseConfig


class TestCLIAdd:
    """Test 'db add' subcommand."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "databases.yaml")

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_add_database_success(self, capsys):
        """Test adding a database configuration successfully."""
        args = Namespace(
            key="production",
            url="http://localhost:8529",
            database="prod_db",
            username="admin",
            password_env="PROD_PASSWORD",
            timeout=60.0,
            description="Production database",
            config_path=self.config_path,
        )

        result = handle_add(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "✓ Database 'production' added successfully" in captured.out
        assert "URL: http://localhost:8529" in captured.out
        assert "Database: prod_db" in captured.out
        assert "Username: admin" in captured.out
        assert "Password env: PROD_PASSWORD" in captured.out
        assert "Timeout: 60.0s" in captured.out
        assert "Description: Production database" in captured.out

        # Verify file was created
        assert os.path.exists(self.config_path)

        # Verify content
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
        assert "production" in config["databases"]
        assert config["databases"]["production"]["url"] == "http://localhost:8529"

    def test_add_database_without_description(self, capsys):
        """Test adding a database without optional description."""
        args = Namespace(
            key="staging",
            url="http://staging:8529",
            database="staging_db",
            username="admin",
            password_env="STAGING_PASSWORD",
            timeout=30.0,
            description=None,
            config_path=self.config_path,
        )

        result = handle_add(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "✓ Database 'staging' added successfully" in captured.out
        assert "Description:" not in captured.out

    def test_add_database_duplicate_key(self, capsys):
        """Test adding a database with duplicate key."""
        # Create existing configuration
        config_data = {
            "databases": {
                "production": {
                    "url": "http://localhost:8529",
                    "database": "prod_db",
                    "username": "admin",
                    "password_env": "PROD_PASSWORD",
                }
            }
        }
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            yaml.dump(config_data, f)

        args = Namespace(
            key="production",
            url="http://new:8529",
            database="new_db",
            username="admin",
            password_env="NEW_PASSWORD",
            timeout=30.0,
            description=None,
            config_path=self.config_path,
        )

        result = handle_add(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "Error: Database 'production' already exists" in captured.err

    def test_add_database_error_handling(self, capsys):
        """Test error handling when adding database fails."""
        # Use invalid path to trigger error
        args = Namespace(
            key="test",
            url="http://localhost:8529",
            database="test_db",
            username="admin",
            password_env="TEST_PASSWORD",
            timeout=30.0,
            description=None,
            config_path="/invalid/path/databases.yaml",
        )

        with patch("mcp_arangodb_async.cli_db.ConfigFileLoader") as mock_loader:
            mock_loader.return_value.load.side_effect = Exception("Test error")
            result = handle_add(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "Error adding database" in captured.err


class TestCLIRemove:
    """Test 'db remove' subcommand."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "databases.yaml")

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_remove_database_success(self, capsys):
        """Test removing a database configuration successfully."""
        # Create existing configuration
        config_data = {
            "databases": {
                "production": {
                    "url": "http://localhost:8529",
                    "database": "prod_db",
                    "username": "admin",
                    "password_env": "PROD_PASSWORD",
                },
                "staging": {
                    "url": "http://staging:8529",
                    "database": "staging_db",
                    "username": "admin",
                    "password_env": "STAGING_PASSWORD",
                }
            }
        }
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            yaml.dump(config_data, f)

        args = Namespace(
            key="production",
            config_path=self.config_path,
        )

        result = handle_remove(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "✓ Database 'production' removed successfully" in captured.out

        # Verify database was removed
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
        assert "production" not in config["databases"]
        assert "staging" in config["databases"]

    def test_remove_database_not_found(self, capsys):
        """Test removing a database that doesn't exist."""
        # Create empty configuration
        config_data = {"databases": {}}
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            yaml.dump(config_data, f)

        args = Namespace(
            key="nonexistent",
            config_path=self.config_path,
        )

        result = handle_remove(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "Error: Database 'nonexistent' not found" in captured.err

    def test_remove_database_error_handling(self, capsys):
        """Test error handling when removing database fails."""
        args = Namespace(
            key="test",
            config_path="/invalid/path/databases.yaml",
        )

        with patch("mcp_arangodb_async.cli_db.ConfigFileLoader") as mock_loader:
            mock_loader.return_value.load.side_effect = Exception("Test error")
            result = handle_remove(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "Error removing database" in captured.err


class TestCLIList:
    """Test 'db list' subcommand."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "databases.yaml")

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_list_databases_success(self, capsys):
        """Test listing databases successfully."""
        # Create configuration with multiple databases
        config_data = {
            "default_database": "production",
            "databases": {
                "production": {
                    "url": "http://localhost:8529",
                    "database": "prod_db",
                    "username": "admin",
                    "password_env": "PROD_PASSWORD",
                    "timeout": 60.0,
                    "description": "Production database"
                },
                "staging": {
                    "url": "http://staging:8529",
                    "database": "staging_db",
                    "username": "admin",
                    "password_env": "STAGING_PASSWORD",
                    "timeout": 30.0,
                }
            }
        }
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            yaml.dump(config_data, f)

        args = Namespace(config_path=self.config_path)

        result = handle_list(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "Configured databases (2):" in captured.out
        assert "Default database: production" in captured.out
        assert "production:" in captured.out
        assert "URL: http://localhost:8529" in captured.out
        assert "Database: prod_db" in captured.out
        assert "Description: Production database" in captured.out
        assert "staging:" in captured.out

    @patch.dict(os.environ, {}, clear=True)
    def test_list_databases_empty(self, capsys):
        """Test listing when no databases are configured."""
        # Create empty YAML file to prevent env var fallback
        config_data = {"databases": {}}
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            yaml.dump(config_data, f)

        args = Namespace(config_path=self.config_path)

        result = handle_list(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "No databases configured" in captured.out

    def test_list_databases_error_handling(self, capsys):
        """Test error handling when listing databases fails."""
        args = Namespace(config_path="/invalid/path/databases.yaml")

        with patch("mcp_arangodb_async.cli_db.ConfigFileLoader") as mock_loader:
            mock_loader.return_value.load.side_effect = Exception("Test error")
            result = handle_list(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "Error listing databases" in captured.err


class TestCLITest:
    """Test 'db test' subcommand."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "databases.yaml")

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_test_connection_success(self, capsys):
        """Test successful database connection test."""
        # Create configuration
        config_data = {
            "databases": {
                "production": {
                    "url": "http://localhost:8529",
                    "database": "prod_db",
                    "username": "admin",
                    "password_env": "PROD_PASSWORD",
                }
            }
        }
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            yaml.dump(config_data, f)

        args = Namespace(
            key="production",
            config_path=self.config_path,
        )

        # Mock the async test_connection method
        with patch("mcp_arangodb_async.cli_db.asyncio.run") as mock_run:
            mock_run.return_value = {
                "connected": True,
                "version": "3.11.0"
            }
            result = handle_test(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "✓ Connection to 'production' successful" in captured.out
        assert "ArangoDB version: 3.11.0" in captured.out

    def test_test_connection_failure(self, capsys):
        """Test failed database connection test."""
        # Create configuration
        config_data = {
            "databases": {
                "production": {
                    "url": "http://localhost:8529",
                    "database": "prod_db",
                    "username": "admin",
                    "password_env": "PROD_PASSWORD",
                }
            }
        }
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            yaml.dump(config_data, f)

        args = Namespace(
            key="production",
            config_path=self.config_path,
        )

        # Mock the async test_connection method
        with patch("mcp_arangodb_async.cli_db.asyncio.run") as mock_run:
            mock_run.return_value = {
                "connected": False,
                "error": "Connection refused"
            }
            result = handle_test(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "✗ Connection to 'production' failed" in captured.err
        assert "Error: Connection refused" in captured.err

    def test_test_connection_not_found(self, capsys):
        """Test connection test for non-existent database."""
        # Create empty configuration
        config_data = {"databases": {}}
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            yaml.dump(config_data, f)

        args = Namespace(
            key="nonexistent",
            config_path=self.config_path,
        )

        result = handle_test(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "Error: Database 'nonexistent' not found" in captured.err

    def test_test_connection_error_handling(self, capsys):
        """Test error handling when testing connection fails."""
        args = Namespace(
            key="test",
            config_path="/invalid/path/databases.yaml",
        )

        with patch("mcp_arangodb_async.cli_db.ConfigFileLoader") as mock_loader:
            mock_loader.return_value.load.side_effect = Exception("Test error")
            result = handle_test(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "Error testing connection" in captured.err


class TestCLIStatus:
    """Test 'db status' subcommand."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "databases.yaml")

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_status_with_default(self, capsys):
        """Test status command with default database set."""
        # Create configuration
        config_data = {
            "default_database": "production",
            "databases": {
                "production": {
                    "url": "http://localhost:8529",
                    "database": "prod_db",
                    "username": "admin",
                    "password_env": "PROD_PASSWORD",
                },
                "staging": {
                    "url": "http://staging:8529",
                    "database": "staging_db",
                    "username": "admin",
                    "password_env": "STAGING_PASSWORD",
                }
            }
        }
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            yaml.dump(config_data, f)

        args = Namespace(config_path=self.config_path)

        result = handle_status(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "Database Resolution Status:" in captured.out
        assert "Default database (from config): production" in captured.out
        assert "Configured databases: 2" in captured.out
        assert "- production" in captured.out
        assert "- staging" in captured.out
        assert "Resolution order:" in captured.out

    @patch.dict(os.environ, {"MCP_DEFAULT_DATABASE": "staging"})
    def test_status_with_env_var(self, capsys):
        """Test status command with environment variable set."""
        # Create configuration
        config_data = {
            "databases": {
                "production": {
                    "url": "http://localhost:8529",
                    "database": "prod_db",
                    "username": "admin",
                    "password_env": "PROD_PASSWORD",
                }
            }
        }
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            yaml.dump(config_data, f)

        args = Namespace(config_path=self.config_path)

        result = handle_status(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "Default database (from MCP_DEFAULT_DATABASE): staging" in captured.out

    def test_status_error_handling(self, capsys):
        """Test error handling when showing status fails."""
        args = Namespace(config_path="/invalid/path/databases.yaml")

        with patch("mcp_arangodb_async.cli_db.ConfigFileLoader") as mock_loader:
            mock_loader.return_value.load.side_effect = Exception("Test error")
            result = handle_status(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "Error showing status" in captured.err

