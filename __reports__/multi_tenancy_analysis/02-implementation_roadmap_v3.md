# mcp-arangodb-async v0.5.0 – Multi-Tenancy Implementation Roadmap (v3 - Final)

**Project**: mcp-arangodb-async – Model Context Protocol Server for ArangoDB  
**Roadmap Date**: 2025-11-22  
**Phase**: Implementation  
**Source**: Architecture Design v3 + Integration Design v3 + Stakeholder Decisions  
**Current Version**: v0.4.0 (MCP Design Patterns, production)  
**Target Version**: v0.5.0 (Multi-Tenancy + Terminology Resolution, production-ready)  
**Timeline**: 4 weeks (test-driven, architecture-first approach)

---

## Executive Summary

This roadmap defines the implementation path for adding multi-tenancy capabilities to mcp-arangodb-async v0.4.0, enabling a single MCP server instance to manage multiple ArangoDB databases and servers through focused database context with optional per-tool override.

**Key Changes from v2**:
- ✅ **Task Context & Rationale**: Added Context (1-4 bullets) and Rationale (1-2 sentences) to all 23 tasks
- ✅ **Enhanced Testing Specifications**: Added 90% coverage target, style compliance, and scope discipline requirements
- ✅ **Enhanced Documentation Gates**: Added style guide compliance and integration analysis requirements
- ✅ **Deferred Features**: Added server-side multi-threading within single session

**Maintained from v2**:
- ✅ **Structure**: 5 phases, 7 milestones, 23 tasks
- ✅ **Timeline**: 4 weeks
- ✅ **Version Target**: v0.4.0 → v0.5.0
- ✅ **Architectural Decisions**: All v3 architecture design decisions preserved

**Stakeholder Decisions**:
- ✅ **Terminology**: "workflow" for design patterns, "focused_database" for multi-tenancy
- ✅ **Session Storage**: `session_state.py` (new file, replaces global variables)
- ✅ **Session Creation**: Implicit on first tool call (no explicit session management tools)
- ✅ **Concurrency**: Sequential within session, concurrent across sessions
- ✅ **Database Override**: Optional `database` parameter on 35 data operation tools
- ✅ **Async Locks**: `asyncio.Lock()` (codebase is fully async)

**Architectural Decision**:
Complete redesign of connection management from singleton pattern to multi-database connection pool with session-based context management. Integrated terminology resolution to eliminate "context" ambiguity between design patterns (workflow context) and multi-tenancy (database context). This avoids retrofitting multi-tenancy and terminology fixes after implementation, preventing technical debt.

---

## Versioning Strategy

**Semantic Versioning (SemVer)**: `Major.Minor.Patch`

**Version Progression**:
- **Major Version**: 0 (pre-1.0 development) → 0 (maintained)
- **Minor Version**: Increments per Phase completion (v0.4.1 → v0.4.2 → v0.4.3 → v0.4.4 → v0.5.0)
- **Patch Version**: Increments per Milestone completion within a Phase
- **Tasks**: Do NOT increment version (tasks are sub-units of milestones)

**Version Management**:
- Configured in `pyproject.toml` with `python-semantic-release`
- Automated version bumping based on conventional commits
- Git tags created automatically on version increments
- PyPI publishing triggered on v0.5.0 tag

---

## Git Workflow

**Branch Hierarchy**: main → dev → feat/multi-arangodb-tenancy → milestone/X.X → task/X.X.X

**Workflow Rules**:
1. All work from `feat/multi-arangodb-tenancy` branch
2. Milestone branches from `feat/multi-arangodb-tenancy`
3. Task branches from milestone branches
4. Merge hierarchy: Task → Milestone → Feature → Dev → Main
5. Conventional commits for automated versioning

---

## Phase 1: Foundation (Week 1)

**Version Target**: v0.4.2 (after Milestone 1.2 complete)

**Objective**: Create core infrastructure components for multi-database connection management and session state management.

### Milestone 1.1: Foundation Core Components (3 days)

**Version Target**: v0.4.1

**Tasks**:

**1.1.1 – SessionState Component**

**Context**:
- Architecture Design v3, Section 2.2: SessionState component specification
- Replaces global state variables (_ACTIVE_CONTEXT, _CURRENT_STAGE, _TOOL_USAGE_STATS) with per-session isolation
- Foundation for all subsequent multi-tenancy features (database context, workflow state)
- Uses asyncio.Lock for thread-safe state mutations (Architecture Design v3, Section 2.2)

**Rationale**: SessionState provides the isolation boundary for multi-database workflows, ensuring that different agents (sessions) can work with different databases and workflow stages without interference.

**Goal**: Create `session_state.py` with SessionState class for per-session state management

**Pre-conditions**: None

**Success Gates**:
- File `mcp_arangodb_async/session_state.py` created
- SessionState class with methods: `initialize_session()`, `set_focused_database()`, `get_focused_database()`, `set_active_workflow()`, `get_active_workflow()`, `set_tool_lifecycle_stage()`, `get_tool_lifecycle_stage()`, `track_tool_usage()`, `get_tool_usage_stats()`, `cleanup_session()`, `cleanup_all()`
- Uses `asyncio.Lock()` for state mutations
- Unit tests pass (session isolation, implicit creation, async lock safety)
- **Coverage Target**: Achieve 90% code coverage for all new code introduced in this task
- **Style Compliance**: Tests follow existing test style and conventions (naming, structure, assertions)
- **Scope Discipline**: Test ONLY SessionState functionality—do not test upstream dependencies, downstream consumers, or speculative use cases outside this task's responsibility

**1.1.2 – MultiDatabaseConnectionManager Component**

**Context**:
- Architecture Design v3, Section 2.1: MultiDatabaseConnectionManager component specification
- Implements connection pooling with async-safe access (asyncio.Lock)
- Supports per-tool database override via dynamic connection retrieval
- Integrates with ConfigFileLoader for database configuration

**Rationale**: MultiDatabaseConnectionManager enables the server to maintain connections to multiple ArangoDB servers and databases simultaneously, providing the foundation for multi-tenancy without connection overhead.

**Goal**: Create `multi_db_manager.py` with connection pooling for multiple databases

**Pre-conditions**: Task 1.1.1 complete (SessionState exists)

**Success Gates**:
- File `mcp_arangodb_async/multi_db_manager.py` created
- MultiDatabaseConnectionManager class with methods: `initialize()`, `get_connection()`, `get_configured_databases()`, `test_connection()`, `register_database()`, `close_all()`
- Uses `asyncio.Lock()` for connection pool mutations
- Unit tests pass (connection pooling, async lock safety, connection reuse)
- **Coverage Target**: Achieve 90% code coverage for all new code introduced in this task
- **Style Compliance**: Tests follow existing test style and conventions (naming, structure, assertions)
- **Scope Discipline**: Test ONLY MultiDatabaseConnectionManager functionality—do not test upstream dependencies, downstream consumers, or speculative use cases outside this task's responsibility

**1.1.3 – ConfigFileLoader Component**

**Context**:
- Architecture Design v3, Section 2.3: ConfigFileLoader component specification
- Loads database configurations from YAML file and environment variables
- Provides backward compatibility with v0.4.0 environment variables (Architecture Design v3, Section 5: Backward Compatibility)
- Security: Passwords stored in environment variables, referenced by name in YAML (Architecture Design v3, Section 3.2)

**Rationale**: ConfigFileLoader decouples database configuration from code, enabling runtime configuration changes via CLI tool and maintaining backward compatibility with existing deployments.

**Goal**: Create `config_loader.py` for YAML configuration and environment variable loading

**Pre-conditions**: Task 1.1.2 complete (MultiDatabaseConnectionManager exists)

**Success Gates**:
- File `mcp_arangodb_async/config_loader.py` created
- ConfigFileLoader class with methods: `load()`, `get_configured_databases()`, `add_database()`, `remove_database()`, `_load_from_env_vars()`, `_save_to_yaml()`
- Backward compatibility with v0.4.0 environment variables
- Unit tests pass (YAML parsing, env var resolution, backward compatibility)
- **Coverage Target**: Achieve 90% code coverage for all new code introduced in this task
- **Style Compliance**: Tests follow existing test style and conventions (naming, structure, assertions)
- **Scope Discipline**: Test ONLY ConfigFileLoader functionality—do not test upstream dependencies, downstream consumers, or speculative use cases outside this task's responsibility

### Milestone 1.2: Foundation Integration (2 days)

**Version Target**: v0.4.2

**Tasks**:

**1.2.1 – Database Resolver**

**Context**:
- Architecture Design v3, Section 2.4: Database resolution algorithm with 6-level priority fallback
- Implements priority: tool arg → focused → config default → env → first configured → hardcoded
- Critical for per-tool database override feature (Architecture Design v3, Section 2.3)

**Rationale**: The database resolver provides a deterministic, predictable algorithm for selecting which database to use for each tool call, enabling both focused database context and per-tool overrides without ambiguity.

**Goal**: Create `db_resolver.py` with 6-level priority database resolution algorithm

**Pre-conditions**: Milestone 1.1 complete

**Success Gates**:
- File `mcp_arangodb_async/db_resolver.py` created
- `resolve_database()` function implements 6-level priority (tool arg → focused → config default → env → first configured → hardcoded)
- Unit tests pass (all 6 priority levels, edge cases)
- **Coverage Target**: Achieve 90% code coverage for all new code introduced in this task
- **Style Compliance**: Tests follow existing test style and conventions (naming, structure, assertions)
- **Scope Discipline**: Test ONLY database resolution logic—do not test upstream dependencies, downstream consumers, or speculative use cases outside this task's responsibility

**1.2.2 – Session ID Extraction**

**Context**:
- Architecture Design v3, Section 2.5: Session ID extraction for stdio vs HTTP transports
- Handles stdio transport (singleton "stdio" session) and HTTP transport (unique ID from request)
- Foundation for session-based state isolation

**Rationale**: Session ID extraction provides a consistent interface for identifying sessions across different MCP transports, enabling the same session state logic to work for both stdio and HTTP deployments.

**Goal**: Create `session_utils.py` with session ID extraction for stdio vs HTTP transports

**Pre-conditions**: Task 1.2.1 complete

**Success Gates**:
- File `mcp_arangodb_async/session_utils.py` created
- `extract_session_id()` function handles stdio ("stdio") and HTTP (unique ID from request)
- Unit tests pass (stdio transport, HTTP transport, edge cases)
- **Coverage Target**: Achieve 90% code coverage for all new code introduced in this task
- **Style Compliance**: Tests follow existing test style and conventions (naming, structure, assertions)
- **Scope Discipline**: Test ONLY session ID extraction logic—do not test upstream dependencies, downstream consumers, or speculative use cases outside this task's responsibility

**1.2.3 – Entry Point Integration**

**Context**:
- Architecture Design v3, Section 2.6: Updated server_lifespan() and call_tool()
- Integrates all foundation components (SessionState, MultiDatabaseConnectionManager, ConfigFileLoader)
- Implements implicit session creation (Architecture Design v3, Section 4.1)
- Implements database resolution in call_tool()

**Rationale**: Entry point integration wires together all foundation components, enabling the MCP server to manage multiple databases and sessions with minimal changes to existing tool handlers.

**Goal**: Update `entry.py` to initialize SessionState and MultiDatabaseConnectionManager in lifespan_context

**Pre-conditions**: Task 1.2.2 complete

**Success Gates**:
- `server_lifespan()` initializes ConfigFileLoader, MultiDatabaseConnectionManager, SessionState
- Components stored in `lifespan_context`
- `call_tool()` implements implicit session creation
- `call_tool()` uses database resolution algorithm
- Integration tests pass (session creation, database resolution, component access)
- **Coverage Target**: Achieve 90% code coverage for all new code introduced in this task
- **Style Compliance**: Tests follow existing test style and conventions (naming, structure, assertions)
- **Scope Discipline**: Test ONLY entry point integration logic—do not test upstream dependencies, downstream consumers, or speculative use cases outside this task's responsibility

---

## Phase 2: Tool Renaming (Week 2, Days 1-3)

**Version Target**: v0.4.3 (after Milestone 2.1 complete)

**Objective**: Rename 3 design pattern tools to eliminate "context" ambiguity.

### Milestone 2.1: Tool Renaming (3 days)

**Version Target**: v0.4.3

**Tasks**:

**2.1.1 – Constants and Models**

**Context**:
- Integration Design v3, Section 4: Tool naming audit identified 3 ambiguous tools
- Terminology resolution: "context" → "workflow" (Architecture Design v3, Changes from v2, Section 1)
- Tool renamings: arango_switch_context → arango_switch_workflow, arango_get_active_context → arango_get_active_workflow, arango_list_contexts → arango_list_workflows

**Rationale**: Renaming eliminates ambiguity between "workflow context" (design patterns) and "database context" (multi-tenancy), preventing confusion in code, documentation, and agent interactions.

**Goal**: Update tool name constants and Pydantic models

**Pre-conditions**: Phase 1 complete

**Success Gates**:
- `tools.py:113-115` updated (ARANGO_SWITCH_WORKFLOW, ARANGO_GET_ACTIVE_WORKFLOW, ARANGO_LIST_WORKFLOWS)
- `models.py:444-465` updated (SwitchWorkflowArgs, GetActiveWorkflowArgs, ListWorkflowsArgs)
- Unit tests pass (model validation)
- **Coverage Target**: Achieve 90% code coverage for all new code introduced in this task
- **Style Compliance**: Tests follow existing test style and conventions (naming, structure, assertions)
- **Scope Discipline**: Test ONLY renamed constants and models—do not test upstream dependencies, downstream consumers, or speculative use cases outside this task's responsibility

**2.1.2 – Handlers and Tests**

**Context**:
- Depends on Task 2.1.1 (constants and models renamed)
- Updates handler registrations and all test references
- Ensures no references to old tool names remain (except in changelog)

**Rationale**: Handler and test updates complete the tool renaming, ensuring the new terminology is consistently applied throughout the codebase and preventing accidental use of old names.

**Goal**: Update handler registrations and all test references

**Pre-conditions**: Task 2.1.1 complete

**Success Gates**:
- `handlers.py:2023, 2074, 2104` updated (handler registrations)
- `tests/test_mcp_integration.py:605-629` updated (test references)
- All tests pass
- Grep for old tool names returns 0 results (except changelog)
- **Coverage Target**: Achieve 90% code coverage for all new code introduced in this task
- **Style Compliance**: Tests follow existing test style and conventions (naming, structure, assertions)
- **Scope Discipline**: Test ONLY handler registrations and renamed tool functionality—do not test upstream dependencies, downstream consumers, or speculative use cases outside this task's responsibility

**2.1.3 – Documentation**

**Context**:
- Depends on Task 2.1.2 (handlers and tests updated)
- Updates all user-facing documentation with new tool names
- Ensures consistency across user guide, tools reference, and README

**Rationale**: Documentation updates ensure users and agents discover and use the correct tool names, preventing confusion and support requests related to deprecated names.

**Goal**: Update all documentation with new tool names

**Pre-conditions**: Task 2.1.2 complete

**Success Gates**:
- `docs/user-guide/mcp-design-patterns.md` updated
- `docs/user-guide/tools-reference.md` updated
- `README.md` examples updated
- Documentation reviewed and approved
- **Style Guide Compliance**: Documentation follows the project style guide (tone, formatting, structure)
- **Integration Analysis**: Documentation integration analysis completed to prevent uncontrolled growth (identify redundancies, consolidation opportunities, and ensure DRY principle)

---

## Phase 3: State Migration (Week 2, Days 4-5 + Week 3, Days 1-2)

**Version Target**: v0.4.5 (after Milestone 3.2 complete)

**Objective**: Migrate 6 design pattern tools + 1 helper from global variables to per-session state.

### Milestone 3.1: State Migration - Tools (2 days)

**Version Target**: v0.4.4

**Tasks**:

**3.1.1 – Workflow Tools Migration**

**Context**:
- Architecture Design v3, Section 2.8: Design pattern tools (3 renamed tools)
- Migrates arango_switch_workflow, arango_get_active_workflow, arango_list_workflows to SessionState
- Replaces global _ACTIVE_CONTEXT with session_state.get_active_workflow()

**Rationale**: Migrating workflow tools to SessionState enables multiple agents to work with different workflows simultaneously without interference, a prerequisite for multi-tenancy.

**Goal**: Migrate arango_switch_workflow, arango_get_active_workflow, arango_list_workflows to SessionState

**Pre-conditions**: Phase 2 complete

**Success Gates**:
- 3 tools access SessionState via `lifespan_context`
- Tools use `session_state.set_active_workflow()` and `session_state.get_active_workflow()`
- Unit tests pass (per-session isolation, workflow persistence)
- **Coverage Target**: Achieve 90% code coverage for all new code introduced in this task
- **Style Compliance**: Tests follow existing test style and conventions (naming, structure, assertions)
- **Scope Discipline**: Test ONLY workflow tool migration—do not test upstream dependencies, downstream consumers, or speculative use cases outside this task's responsibility

**3.1.2 – Lifecycle Tools Migration**

**Context**:
- Architecture Design v3, Section 2.8: Design pattern tools (lifecycle stage management)
- Migrates arango_advance_workflow_stage, arango_unload_tools to SessionState
- Replaces global _CURRENT_STAGE with session_state.get_tool_lifecycle_stage()

**Rationale**: Migrating lifecycle tools to SessionState enables multiple agents to progress through different workflow stages independently, supporting concurrent multi-database workflows.

**Goal**: Migrate arango_advance_workflow_stage, arango_unload_tools to SessionState

**Pre-conditions**: Task 3.1.1 complete

**Success Gates**:
- 2 tools access SessionState via `lifespan_context`
- Tools use `session_state.set_tool_lifecycle_stage()` and `session_state.get_tool_lifecycle_stage()`
- Unit tests pass (per-session isolation, stage persistence)
- **Coverage Target**: Achieve 90% code coverage for all new code introduced in this task
- **Style Compliance**: Tests follow existing test style and conventions (naming, structure, assertions)
- **Scope Discipline**: Test ONLY lifecycle tool migration—do not test upstream dependencies, downstream consumers, or speculative use cases outside this task's responsibility

**3.1.3 – Usage Stats Migration**

**Context**:
- Architecture Design v3, Section 2.8: Design pattern tools (tool usage tracking)
- Migrates arango_get_tool_usage_stats and _track_tool_usage helper to SessionState
- Replaces global _TOOL_USAGE_STATS with session_state.get_tool_usage_stats()

**Rationale**: Migrating usage stats to SessionState enables per-session analytics, allowing agents to track their own tool usage without seeing other agents' statistics.

**Goal**: Migrate arango_get_tool_usage_stats and _track_tool_usage helper to SessionState

**Pre-conditions**: Task 3.1.2 complete

**Success Gates**:
- 1 tool + 1 helper access SessionState via `lifespan_context`
- Tools use `session_state.track_tool_usage()` and `session_state.get_tool_usage_stats()`
- Unit tests pass (per-session isolation, stats tracking)
- **Coverage Target**: Achieve 90% code coverage for all new code introduced in this task
- **Style Compliance**: Tests follow existing test style and conventions (naming, structure, assertions)
- **Scope Discipline**: Test ONLY usage stats migration—do not test upstream dependencies, downstream consumers, or speculative use cases outside this task's responsibility

### Milestone 3.2: State Migration - Cleanup (2 days)

**Version Target**: v0.4.5

**Tasks**:

**3.2.1 – Global Variable Removal**

**Context**:
- Depends on Milestone 3.1 (all 6 tools + 1 helper migrated to SessionState)
- Removes global variables _ACTIVE_CONTEXT, _CURRENT_STAGE, _TOOL_USAGE_STATS from handlers.py
- Completes transition from global state to per-session state

**Rationale**: Removing global variables eliminates the risk of cross-session interference and ensures all state management goes through SessionState, enforcing proper isolation.

**Goal**: Remove global variables from handlers.py

**Pre-conditions**: Milestone 3.1 complete

**Success Gates**:
- `_ACTIVE_CONTEXT` deleted from `handlers.py:2018`
- `_CURRENT_STAGE` deleted from `handlers.py:2173`
- `_TOOL_USAGE_STATS` deleted from `handlers.py:2174`
- Grep for global variables returns 0 results
- All tests pass

**3.2.2 – Verification**

**Context**:
- Depends on Task 3.2.1 (global variables removed)
- Verifies concurrent sessions have independent state
- Integration Design v3, Section 6.1: Risk mitigation for workflow context reset

**Rationale**: Verification ensures that the state migration achieved its goal of session isolation, preventing regressions where one agent's actions affect another agent's state.

**Goal**: Verify concurrent sessions have independent state

**Pre-conditions**: Task 3.2.1 complete

**Success Gates**:
- Test `test_concurrent_sessions_independent_state()` passes
- Test `test_workflow_switch_preserves_focused_database()` passes
- Integration tests pass (2 concurrent sessions, verify isolation)
- **Coverage Target**: Achieve 90% code coverage for all new code introduced in this task
- **Style Compliance**: Tests follow existing test style and conventions (naming, structure, assertions)
- **Scope Discipline**: Test ONLY concurrent session isolation—do not test upstream dependencies, downstream consumers, or speculative use cases outside this task's responsibility

---

## Phase 4: Database Override (Week 3, Days 3-5 + Week 4, Days 1-2)

**Version Target**: v0.4.7 (after Milestone 4.2 complete)

**Objective**: Add optional `database` parameter to 35 data operation tools and implement 6 multi-tenancy tools + CLI tool.

### Milestone 4.1: Database Override - Tool Models (2 days)

**Version Target**: v0.4.6

**Tasks**:

**4.1.1 – Tool Models Update**

**Context**:
- Architecture Design v3, Section 2.9: Data operation tools (35 tools requiring database parameter)
- Integration Design v3, Section 3: Per-tool database override for cross-database workflows
- Categories: Core Data (9), Indexing (3), Validation & Bulk (4), Graph (13), Schema & Query (6)

**Rationale**: Adding the optional database parameter to tool models enables agents to execute cross-database operations (e.g., data migration) without changing the focused database, maintaining workflow context.

**Goal**: Add optional `database` parameter to 35 tool models in models.py

**Pre-conditions**: Phase 3 complete

**Success Gates**:
- 35 tool models updated with `database: Optional[str] = Field(default=None, description="Database override")`
- Categories: Core Data (9), Indexing (3), Validation & Bulk (4), Graph (13), Schema & Query (6)
- Unit tests pass (model validation, optional parameter)
- **Coverage Target**: Achieve 90% code coverage for all new code introduced in this task
- **Style Compliance**: Tests follow existing test style and conventions (naming, structure, assertions)
- **Scope Discipline**: Test ONLY tool model updates—do not test upstream dependencies, downstream consumers, or speculative use cases outside this task's responsibility

**4.1.2 – Handler Updates**

**Context**:
- Depends on Task 4.1.1 (tool models updated with database parameter)
- Architecture Design v3, Section 2.4: Database resolution algorithm
- Integration Design v3, Section 3.5: Per-tool override does NOT mutate focused_database state

**Rationale**: Handler updates implement the database resolution logic, enabling per-tool overrides while preserving focused database state, a critical requirement for predictable multi-database workflows.

**Goal**: Update 35 tool handlers to use database resolution

**Pre-conditions**: Task 4.1.1 complete

**Success Gates**:
- 35 handlers call `resolve_database()` to get target database
- 35 handlers call `db_manager.get_connection(target_db_key)` to get database connection
- Unit tests pass (database resolution, per-tool override)
- Test `test_per_tool_override_does_not_mutate_state()` passes
- **Coverage Target**: Achieve 90% code coverage for all new code introduced in this task
- **Style Compliance**: Tests follow existing test style and conventions (naming, structure, assertions)
- **Scope Discipline**: Test ONLY handler database resolution logic—do not test upstream dependencies, downstream consumers, or speculative use cases outside this task's responsibility

### Milestone 4.2: Multi-Tenancy Tools (3 days)

**Version Target**: v0.4.7

**Tasks**:

**4.2.1 – MCP Tools Implementation**

**Context**:
- Architecture Design v3, Section 2.7: Multi-tenancy MCP tools (6 tools)
- Tools: arango_set_focused_database, arango_get_focused_database, arango_list_available_databases, arango_get_database_resolution, arango_test_database_connection, arango_get_multi_database_status
- Provides agent-facing interface for database selection and status reporting

**Rationale**: Multi-tenancy MCP tools give agents visibility and control over database selection, enabling them to understand and manage multi-database workflows effectively.

**Goal**: Implement 6 multi-tenancy MCP tools

**Pre-conditions**: Milestone 4.1 complete

**Success Gates**:
- Tools implemented: arango_set_focused_database, arango_get_focused_database, arango_list_available_databases, arango_get_database_resolution, arango_test_database_connection, arango_get_multi_database_status
- Tool models created in `models.py`
- Tool handlers created in `handlers.py`
- Unit tests pass (all 6 tools)
- **Coverage Target**: Achieve 90% code coverage for all new code introduced in this task
- **Style Compliance**: Tests follow existing test style and conventions (naming, structure, assertions)
- **Scope Discipline**: Test ONLY multi-tenancy MCP tools—do not test upstream dependencies, downstream consumers, or speculative use cases outside this task's responsibility

**4.2.2 – CLI Tool Implementation**

**Context**:
- Architecture Design v3, Section 2.10: CLI tool with 5 subcommands
- Subcommands: add, remove, list, test, status
- Uses argparse (already in codebase)
- Admin-only (requires file system access to modify YAML)

**Rationale**: The CLI tool provides secure, admin-controlled configuration management, enabling database additions/removals without code changes or server restarts.

**Goal**: Implement `mcp-arangodb-async db` CLI tool with 5 subcommands

**Pre-conditions**: Task 4.2.1 complete

**Success Gates**:
- `__main__.py` extended with `db` subcommand
- Subcommands: add, remove, list, test, status
- Uses `argparse` (already in codebase)
- CLI tests pass (all 5 subcommands)
- **Coverage Target**: Achieve 90% code coverage for all new code introduced in this task
- **Style Compliance**: Tests follow existing test style and conventions (naming, structure, assertions)
- **Scope Discipline**: Test ONLY CLI tool functionality—do not test upstream dependencies, downstream consumers, or speculative use cases outside this task's responsibility

**4.2.3 – Documentation**

**Context**:
- Depends on Tasks 4.2.1 and 4.2.2 (MCP tools and CLI tool implemented)
- Documents 6 multi-tenancy tools, database parameter on 35 tools, and CLI tool
- Updates user guide, tools reference, CLI reference, and README

**Rationale**: Comprehensive documentation ensures users and agents can discover and effectively use multi-tenancy features, reducing support burden and increasing adoption.

**Goal**: Document multi-tenancy tools and CLI tool

**Pre-conditions**: Task 4.2.2 complete

**Success Gates**:
- `docs/user-guide/tools-reference.md` updated (6 multi-tenancy tools, database parameter on 35 tools)
- `docs/user-guide/cli-reference.md` created (CLI tool documentation)
- `README.md` updated (multi-tenancy examples)
- Documentation reviewed and approved
- **Style Guide Compliance**: Documentation follows the project style guide (tone, formatting, structure)
- **Integration Analysis**: Documentation integration analysis completed to prevent uncontrolled growth (identify redundancies, consolidation opportunities, and ensure DRY principle)

---

## Phase 5: Verification & Release (Week 4, Days 3-5)

**Version Target**: v0.5.0 (final release)

**Objective**: Comprehensive testing, documentation, and release preparation.

### Milestone 5.1: Verification & Release (3 days)

**Version Target**: v0.5.0

**Tasks**:

**5.1.1 – Test Suite Execution**

**Context**:
- Depends on Phase 4 complete (all features implemented)
- Runs full test suite to verify no regressions from v0.4.0
- Ensures test coverage ≥90% for entire project

**Rationale**: Comprehensive test suite execution provides confidence that the multi-tenancy feature works correctly and doesn't break existing functionality, a prerequisite for production release.

**Goal**: Run full test suite and verify all tests pass

**Pre-conditions**: Phase 4 complete

**Success Gates**:
- All unit tests pass (pytest tests/)
- All integration tests pass
- Test coverage ≥90%
- No regressions from v0.4.0
- **Coverage Target**: Achieve 90% code coverage for all new code introduced in this task
- **Style Compliance**: Tests follow existing test style and conventions (naming, structure, assertions)
- **Scope Discipline**: Test ONLY test suite execution and coverage reporting—do not test upstream dependencies, downstream consumers, or speculative use cases outside this task's responsibility

**5.1.2 – Integration Testing**

**Context**:
- Depends on Task 5.1.1 (test suite passes)
- Tests concurrent sessions, cross-database workflows, backward compatibility
- Integration Design v3, Section 3: Cross-database workflow use cases (analytics, migration, schema validation)

**Rationale**: Integration testing validates real-world multi-tenancy scenarios, ensuring the feature works end-to-end in production-like conditions.

**Goal**: Test concurrent sessions, cross-database workflows, backward compatibility

**Pre-conditions**: Task 5.1.1 complete

**Success Gates**:
- Test concurrent sessions (2 MCP clients, verify independent state)
- Test cross-database workflow (data migration scenario)
- Test backward compatibility (single-database deployment with env vars)
- Stress test (10 concurrent sessions)
- Performance test (connection pool efficiency)
- **Coverage Target**: Achieve 90% code coverage for all new code introduced in this task
- **Style Compliance**: Tests follow existing test style and conventions (naming, structure, assertions)
- **Scope Discipline**: Test ONLY integration scenarios—do not test upstream dependencies, downstream consumers, or speculative use cases outside this task's responsibility

**5.1.3 – Release Preparation**

**Context**:
- Depends on Task 5.1.2 (integration tests pass)
- Updates changelog, creates migration guide, prepares release
- Final version bump to v0.5.0

**Rationale**: Release preparation ensures users have the information and resources needed to upgrade smoothly, reducing support burden and increasing adoption.

**Goal**: Update changelog, create migration guide, prepare release

**Pre-conditions**: Task 5.1.2 complete

**Success Gates**:
- `CHANGELOG.md` updated with v0.5.0 release notes
- `docs/migration/v0.4-to-v0.5.md` created (migration guide)
- `docs/deployment/multi-database-setup.md` created (deployment guide)
- Version bumped to v0.5.0 in `pyproject.toml`
- Git tag v0.5.0 created
- PyPI release published
- **Style Guide Compliance**: Documentation follows the project style guide (tone, formatting, structure)
- **Integration Analysis**: Documentation integration analysis completed to prevent uncontrolled growth (identify redundancies, consolidation opportunities, and ensure DRY principle)

---

## Deferred Features (v0.6.0+)

**Global Tool Usage Stats Aggregation**:
- **Rationale**: v0.5.0 implements per-session stats only; global aggregation deferred for simplicity
- **Timeline**: v0.6.0 release
- **Benefit**: Cross-session analytics for server administrators
- **Implementation**: Aggregate stats from all sessions, expose via new MCP tool

**Database Connection Pool Size Limits**:
- **Rationale**: v0.5.0 has unlimited connection pool; limits deferred until production usage patterns known
- **Timeline**: v0.6.0 release
- **Benefit**: Prevent connection pool exhaustion under high load
- **Implementation**: Add `max_connections_per_database` config parameter

**Automatic Session Cleanup on Timeout**:
- **Rationale**: v0.5.0 cleans up sessions on disconnect only; timeout-based cleanup deferred
- **Timeline**: v0.6.0 release
- **Benefit**: Prevent memory leaks from abandoned sessions
- **Implementation**: Background task to clean up sessions inactive for >1 hour

**Server-Side Multi-Threading Within Single Session**:
- **Rationale**: v0.5.0 implements sequential processing within sessions; concurrent query execution within single session deferred
- **Timeline**: v0.7.0 release (requires significant architectural changes)
- **Benefit**: Allows a single agent to execute multiple long-running queries in parallel without blocking
- **Technical Considerations**: Requires thread-safe session state management, ArangoDB connection pooling per session, and careful handling of python-arango's non-thread-safe components
- **Implementation**: Introduce per-session thread pool, thread-safe SessionState with fine-grained locking, and connection pool per session

---

## Success Criteria for v0.5.0

**Functional Requirements**:
- ✅ Single MCP server instance supports multiple databases and servers
- ✅ Focused database context with optional per-tool override
- ✅ 6 multi-tenancy MCP tools (set/get focused database, list, test, status, resolution)
- ✅ CLI tool with 5 subcommands (add, remove, list, test, status)
- ✅ 35 data operation tools support optional `database` parameter
- ✅ 3 design pattern tools renamed (arango_switch_workflow, arango_get_active_workflow, arango_list_workflows)
- ✅ Backward compatibility with v0.4.0 (environment variables work)

**Quality Requirements**:
- ✅ Test coverage ≥90%
- ✅ All tests pass (unit, integration, stress, performance)
- ✅ No regressions from v0.4.0
- ✅ Documentation complete (user guide, CLI reference, migration guide, deployment guide)
- ✅ Security best practices followed (passwords in env vars, CLI admin-only)

---

## Topological Ordering for Parallel Development

**Critical Path** (must complete in order):
1. Phase 1 (Foundation) → Phase 2 (Tool Renaming) → Phase 3 (State Migration) → Phase 4 (Database Override) → Phase 5 (Verification)

**Parallel Opportunities**:
- Milestone 1.1 tasks (1.1.1, 1.1.2, 1.1.3) can run in parallel (independent components)
- Milestone 1.2 tasks (1.2.1, 1.2.2) can run in parallel (independent utilities)
- Milestone 3.1 tasks (3.1.1, 3.1.2, 3.1.3) can run in parallel (independent tool migrations)
- Milestone 4.1 tasks (4.1.1, 4.1.2) must run sequentially (models before handlers)
- Milestone 4.2 tasks (4.2.1, 4.2.2) can run in parallel (MCP tools and CLI tool are independent)

---

**Report Version**: v3 (Final)
**Status**: Ready for Implementation
**Next Steps**: Create GitHub Issues for each task, assign to team members, begin Phase 1 (Foundation)


