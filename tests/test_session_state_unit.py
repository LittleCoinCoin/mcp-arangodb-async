"""Unit tests for SessionState component."""

import pytest
import asyncio
from datetime import datetime
from mcp_arangodb_async.session_state import SessionState


class TestSessionState:
    """Test SessionState component for per-session state management."""

    def setup_method(self):
        """Set up test fixtures."""
        self.session_state = SessionState()

    def test_initialize_session(self):
        """Test session initialization with default values."""
        session_id = "test_session_1"
        
        self.session_state.initialize_session(session_id)
        
        assert self.session_state.get_focused_database(session_id) is None
        assert self.session_state.get_active_workflow(session_id) == "baseline"
        assert self.session_state.get_tool_lifecycle_stage(session_id) == "setup"
        assert self.session_state.get_tool_usage_stats(session_id) == {}

    def test_has_session(self):
        """Test session existence check."""
        session_id = "test_session_1"
        
        assert not self.session_state.has_session(session_id)
        
        self.session_state.initialize_session(session_id)
        
        assert self.session_state.has_session(session_id)

    @pytest.mark.asyncio
    async def test_set_and_get_focused_database(self):
        """Test setting and getting focused database."""
        session_id = "test_session_1"
        self.session_state.initialize_session(session_id)
        
        await self.session_state.set_focused_database(session_id, "production")
        
        assert self.session_state.get_focused_database(session_id) == "production"

    @pytest.mark.asyncio
    async def test_set_and_get_active_workflow(self):
        """Test setting and getting active workflow."""
        session_id = "test_session_1"
        self.session_state.initialize_session(session_id)
        
        await self.session_state.set_active_workflow(session_id, "data_migration")
        
        assert self.session_state.get_active_workflow(session_id) == "data_migration"

    @pytest.mark.asyncio
    async def test_set_and_get_tool_lifecycle_stage(self):
        """Test setting and getting tool lifecycle stage."""
        session_id = "test_session_1"
        self.session_state.initialize_session(session_id)
        
        await self.session_state.set_tool_lifecycle_stage(session_id, "data_loading")
        
        assert self.session_state.get_tool_lifecycle_stage(session_id) == "data_loading"

    def test_track_tool_usage(self):
        """Test tool usage tracking."""
        session_id = "test_session_1"
        self.session_state.initialize_session(session_id)

        # Track first usage
        self.session_state.track_tool_usage(session_id, "arango_query")

        stats = self.session_state.get_tool_usage_stats(session_id)
        assert "arango_query" in stats
        assert stats["arango_query"]["use_count"] == 1
        assert "first_used" in stats["arango_query"]
        assert "last_used" in stats["arango_query"]

        # Track second usage
        self.session_state.track_tool_usage(session_id, "arango_query")

        stats = self.session_state.get_tool_usage_stats(session_id)
        assert stats["arango_query"]["use_count"] == 2

    def test_track_tool_usage_without_initialization(self):
        """Test tool usage tracking for uninitialized session."""
        session_id = "test_session_uninit"

        # Track usage without initializing session first
        self.session_state.track_tool_usage(session_id, "arango_query")

        stats = self.session_state.get_tool_usage_stats(session_id)
        assert "arango_query" in stats
        assert stats["arango_query"]["use_count"] == 1

    def test_cleanup_session(self):
        """Test session cleanup."""
        session_id = "test_session_1"
        self.session_state.initialize_session(session_id)
        
        self.session_state.cleanup_session(session_id)
        
        assert not self.session_state.has_session(session_id)
        assert self.session_state.get_focused_database(session_id) is None
        assert self.session_state.get_active_workflow(session_id) is None

    def test_cleanup_all(self):
        """Test cleanup of all sessions."""
        self.session_state.initialize_session("session_1")
        self.session_state.initialize_session("session_2")
        self.session_state.initialize_session("session_3")
        
        self.session_state.cleanup_all()
        
        assert not self.session_state.has_session("session_1")
        assert not self.session_state.has_session("session_2")
        assert not self.session_state.has_session("session_3")

    def test_session_isolation(self):
        """Test that sessions are isolated from each other."""
        session_1 = "session_1"
        session_2 = "session_2"
        
        self.session_state.initialize_session(session_1)
        self.session_state.initialize_session(session_2)
        
        # Set different values for each session
        asyncio.run(self.session_state.set_focused_database(session_1, "production"))
        asyncio.run(self.session_state.set_focused_database(session_2, "staging"))
        
        asyncio.run(self.session_state.set_active_workflow(session_1, "data_migration"))
        asyncio.run(self.session_state.set_active_workflow(session_2, "analytics"))
        
        # Verify isolation
        assert self.session_state.get_focused_database(session_1) == "production"
        assert self.session_state.get_focused_database(session_2) == "staging"
        assert self.session_state.get_active_workflow(session_1) == "data_migration"
        assert self.session_state.get_active_workflow(session_2) == "analytics"

    @pytest.mark.asyncio
    async def test_concurrent_access_safety(self):
        """Test async lock safety with concurrent access."""
        session_id = "test_session_1"
        self.session_state.initialize_session(session_id)
        
        # Simulate concurrent writes
        async def set_database(db_name: str):
            await self.session_state.set_focused_database(session_id, db_name)
            await asyncio.sleep(0.01)  # Simulate some work
        
        # Run concurrent operations
        await asyncio.gather(
            set_database("db1"),
            set_database("db2"),
            set_database("db3")
        )
        
        # Should have one of the values (last write wins)
        result = self.session_state.get_focused_database(session_id)
        assert result in ["db1", "db2", "db3"]

