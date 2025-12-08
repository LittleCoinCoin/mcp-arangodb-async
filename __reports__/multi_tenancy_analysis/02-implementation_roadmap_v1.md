# mcp-arangodb-async v0.4.0 – Multi-Tenancy Implementation Roadmap (v1)

**Project**: mcp-arangodb-async – Model Context Protocol Server for ArangoDB  
**Roadmap Date**: 2025-11-08  
**Phase**: Planning  
**Source**: Architecture Design v1 + Stakeholder Decisions + Test-Driven Development Workflow  
**Current Version**: v0.3.2 (single-database, production)  
**Target Version**: v0.4.0 (multi-tenancy MVP, production-ready)  
**Timeline**: 5.5 weeks (test-driven, architecture-first approach)

---

## Executive Summary

This roadmap defines the implementation path for adding multi-tenancy capabilities to mcp-arangodb-async, enabling a single MCP server instance to manage multiple ArangoDB databases and servers through focused database context with optional per-tool override.

**Stakeholder Decisions**:
- ✅ **Multi-Tenancy Pattern**: Option A-Enhanced (Focused Database Context with Optional Override) - Single server instance, session-based context, no context window pollution
- ✅ **Configuration Management**: Approach 3B (CLI-based) - Secure admin-controlled configuration using `argparse`, YAML config file with environment variable references
- ✅ **CLI Framework**: Use `argparse` (already in codebase at `__main__.py:15`) - No new dependencies
- ✅ **CLI Command Name**: `mcp-arangodb-async db` - Clear, short, memorable
- ✅ **Status Reporting**: 6 MCP tools (3 context management + 3 comprehensive status reporting) - Full database resolution visibility
- ✅ **Multi-Server Support**: Yes - Supports multiple ArangoDB server instances (different URLs/hosts)
- ✅ **Backward Compatibility**: Mandatory - Existing environment variable configuration must continue to work

**Architectural Decision**:
Complete redesign of connection management architecture from singleton pattern to multi-database connection pool with session-based context management. This avoids retrofitting multi-tenancy support after implementation, which creates technical debt and maintenance challenges. The new architecture integrates multi-database support as a first-class concern from the ground up.

---

## Changes from v0

### 1. Git Workflow Updated with Feature Branch

**Change**: Added `feat/multi-arangodb-tenancy` feature branch between `dev` and milestone branches.

**Rationale**: Follows organizational git workflow standards where all feature work branches from a dedicated feature branch, not directly from `dev`. This provides better isolation and cleaner merge history.

**Impact**:
- All milestone branches now branch from `feat/multi-arangodb-tenancy`
- Milestone branches merge back to `feat/multi-arangodb-tenancy` (not `dev`)
- `feat/multi-arangodb-tenancy` merges to `dev` only when v0.4.0 is complete
- Updated merge hierarchy and workflow rules in Section 3

### 2. Test Implementation Tasks Added

**Change**: Added test implementation task (X.X.2) after every test definition task (X.X.1), before code implementation begins.

**Rationale**: Test-driven development requires tests to be implemented and passing BEFORE code implementation. The v0 roadmap had test definition but jumped directly to code implementation without implementing the tests first.

**Impact**:
- 6 new test implementation tasks added (one per milestone with test definition)
- Task numbering shifted for all code implementation tasks (X.X.2 → X.X.3, X.X.3 → X.X.4, etc.)
- Total tasks increased from 20 to 26 (before documentation tasks)
- Timeline unchanged (test implementation is small, 0.5-1 day per milestone)

### 3. Documentation Integrated Throughout Implementation

**Change**: Removed monolithic "Documentation & Release" milestone. Distributed documentation tasks to specific milestones where user-facing or developer-facing changes occur.

**Rationale**: Incremental documentation as features are implemented is more maintainable than bulk documentation at the end. Documentation written alongside implementation is more accurate and complete.

**Impact**:
- Milestone 2.1 (CLI Tool): Added CLI Tool User Documentation task
- Milestone 3.2 (Status Reporting Tools): Added MCP Tools API Reference Documentation task
- Milestone 4.2 (Tool Model Updates): Added Developer Architecture Documentation task
- Milestone 5.2 renamed to "Release Preparation" with only release-specific documentation (migration guide, deployment guide, troubleshooting, CHANGELOG)
- 3 new documentation tasks added
- Total tasks increased from 26 to 29
- Timeline unchanged (documentation tasks are small, 0.25-0.5 days each)

**Documentation Task Pattern**:
Each documentation task follows this structure:
- Study `docs/STYLE_GUIDE.md` for documentation writing standards
- Determine optimal integration point in existing documentation structure
- Identify CRUD operation (CREATE new section, UPDATE existing section, DELETE outdated content)
- Write documentation following repo's style guide
- Integrate documentation into existing docs at identified integration point
- Documentation reviewed and approved

---

## Versioning Strategy

**Semantic Versioning (SemVer)**: `Major.Minor.Patch`

**Version Progression**:
- **Major Version**: 0 (pre-1.0 development) → 0 (maintained)
  - Major=0 enforced until v1.0.0 release (API stabilization)
  - Breaking changes allowed during Major=0 phase (pre-production)
  - Major=1 signals production-ready stable API

- **Minor Version**: Increments per Phase completion
  - Phase 1 complete → v0.3.3 (Core Infrastructure)
  - Phase 2 complete → v0.3.4 (CLI Tool)
  - Phase 3 complete → v0.3.5 (Context Management & Status Tools)
  - Phase 4 complete → v0.3.6 (Tool Model Updates)
  - Final release → v0.4.0 (Multi-Tenancy MVP)

- **Patch Version**: Increments per Milestone completion within a Phase
  - Milestone 1.1 complete → v0.3.3 (first milestone of Phase 1)
  - Milestone 1.2 complete → v0.3.3 (second milestone of Phase 1, no version bump)
  - Milestone 2.1 complete → v0.3.4 (first milestone of Phase 2)
  - Milestone 3.1 complete → v0.3.5 (first milestone of Phase 3)
  - Milestone 4.1 complete → v0.3.6 (first milestone of Phase 4)
  - Milestone 5.1 complete → v0.4.0 (final release)

- **Tasks**: Do NOT increment version (tasks are sub-units of milestones)

**Version Management**:
- Configured in `pyproject.toml` with `python-semantic-release`
- Automated version bumping based on conventional commits
- Git tags created automatically on version increments
- PyPI publishing triggered on v0.4.0 tag

---

## Git Workflow

**mcp-arangodb-async-Specific Branching Strategy** (Project Variation)

**Branch Hierarchy**:
```
main (production, v0.4.0 release only)
  └── dev (development integration branch)
      └── feat/multi-arangodb-tenancy (multi-tenancy feature branch)
          ├── milestone/1.1-core-infrastructure
          │   ├── task/1.1.1-test-definition
          │   ├── task/1.1.2-test-implementation
          │   ├── task/1.1.3-multi-db-manager
          │   ├── task/1.1.4-session-context-manager
          │   └── task/1.1.5-config-loader
          ├── milestone/2.1-cli-tool
          │   ├── task/2.1.1-test-definition
          │   ├── task/2.1.2-test-implementation
          │   ├── task/2.1.3-cli-implementation
          │   ├── task/2.1.4-cli-integration
          │   └── task/2.1.5-cli-documentation
          ├── milestone/3.1-context-tools
          │   ├── task/3.1.1-test-definition
          │   ├── task/3.1.2-test-implementation
          │   └── task/3.1.3-context-tools-implementation
          ├── milestone/3.2-status-tools
          │   ├── task/3.2.1-test-definition
          │   ├── task/3.2.2-test-implementation
          │   ├── task/3.2.3-status-tools-implementation
          │   └── task/3.2.4-mcp-tools-documentation
          ├── milestone/4.1-database-resolution
          │   ├── task/4.1.1-test-definition
          │   ├── task/4.1.2-test-implementation
          │   └── task/4.1.3-database-resolution-implementation
          ├── milestone/4.2-tool-model-updates
          │   ├── task/4.2.1-test-definition
          │   ├── task/4.2.2-test-implementation
          │   ├── task/4.2.3-tool-model-updates-implementation
          │   └── task/4.2.4-architecture-documentation
          ├── milestone/5.1-testing-security
          │   ├── task/5.1.1-e2e-tests
          │   ├── task/5.1.2-security-audit
          │   └── task/5.1.3-performance-testing
          └── milestone/5.2-release-preparation
              ├── task/5.2.1-migration-guide
              ├── task/5.2.2-deployment-guide
              ├── task/5.2.3-troubleshooting-guide
              └── task/5.2.4-release-preparation
```

**Workflow Rules**:

1. **All work from `feat/multi-arangodb-tenancy` branch** (not `dev`)
   - `dev` is the integration branch for all development work
   - `feat/multi-arangodb-tenancy` is the feature branch for multi-tenancy work
   - `main` is production-only, receives merges only at v0.4.0 release

2. **Milestone branches from `feat/multi-arangodb-tenancy`**
   - Branch naming: `milestone/<milestone-id>-<short-description>`
   - Example: `milestone/1.1-core-infrastructure`
   - Created when milestone work begins
   - Deleted after merge back to `feat/multi-arangodb-tenancy`

3. **Task branches from milestone branches**
   - Branch naming: `task/<task-id>-<short-description>`
   - Example: `task/1.1.1-test-definition`
   - Created when task work begins
   - Deleted after merge back to milestone branch

4. **Merge Hierarchy**:
   - Task branches → Milestone branch (when task complete)
   - Milestone branch → `feat/multi-arangodb-tenancy` (when ALL milestone tasks complete)
   - `feat/multi-arangodb-tenancy` → `dev` (when ALL phases complete and v0.4.0 ready)
   - `dev` → `main` (final production release)

5. **Merge Criteria**:
   - **Task → Milestone**: Task success gates met, task tests pass
   - **Milestone → feat/multi-arangodb-tenancy**: All milestone tasks complete, all milestone tests pass, no regressions
   - **feat/multi-arangodb-tenancy → dev**: ALL tests pass (regression, unit, integration, performance), ready for release
   - **dev → main**: Final production release approval

6. **Conventional Commits**:
   - Follow organization's conventional commit format
   - Enables automated semantic versioning
   - See `git-workflow.md` for commit message standards

**Note**: This is a mcp-arangodb-async-specific variation of the organization's standard git workflow, optimized for milestone-based development with strict quality gates.

---

## Phase 1: Core Infrastructure (Weeks 1-1.5)

**Version Target**: v0.3.3 (after all Phase 1 milestones complete)

**Objective**: Build foundational multi-database connection management and session context infrastructure with comprehensive test coverage.

### Milestone 1.1: Core Infrastructure Implementation (1.5 weeks)

**Version Target**: v0.3.3 (first and only milestone of Phase 1)

**Tasks**:

**1.1.1 – Test Definition for Core Infrastructure**
- **Goal**: Define comprehensive test suite for MultiDatabaseConnectionManager, SessionContextManager, and ConfigFileLoader before implementation
- **Pre-conditions**: Architecture Design v1 approved
- **Success Gates**:
  - Test definition report created following org's reporting guidelines
  - Unit tests defined for MultiDatabaseConnectionManager (connection pooling, thread safety, configuration loading)
  - Unit tests defined for SessionContextManager (session lifecycle, focused database management, thread safety)
  - Unit tests defined for ConfigFileLoader (YAML parsing, Pydantic validation, environment variable integration)
  - Integration tests defined for component interaction (config load → connection creation → session management)
  - Edge case tests defined (invalid YAML, missing env vars, connection failures, concurrent access)
  - User review and approval of test definition report

**1.1.2 – Test Implementation for Core Infrastructure**
- **Goal**: Implement all tests defined in 1.1.1 before code implementation begins
- **Pre-conditions**: Task 1.1.1 complete (test definition approved)
- **Success Gates**:
  - All unit tests from 1.1.1 implemented for MultiDatabaseConnectionManager
  - All unit tests from 1.1.1 implemented for SessionContextManager
  - All unit tests from 1.1.1 implemented for ConfigFileLoader
  - All integration tests from 1.1.1 implemented
  - All edge case tests from 1.1.1 implemented
  - Tests run and FAIL (expected - code not implemented yet)
  - Test execution report generated showing failing tests
  - User review and approval of test implementation

**1.1.3 – MultiDatabaseConnectionManager Implementation**
- **Goal**: Implement multi-database connection pool with thread-safe access and configuration management
- **Pre-conditions**: Task 1.1.2 complete (tests implemented and failing)
- **Success Gates**:
  - `mcp_arangodb_async/multi_db_manager.py` created
  - `MultiDatabaseConnectionManager` class implemented with connection pooling
  - Thread-safe connection retrieval using `threading.Lock`
  - Configuration loading from YAML file and environment variables
  - Connection lifecycle management (create, reuse, cleanup)
  - All unit tests from 1.1.2 pass for MultiDatabaseConnectionManager
  - Code follows existing codebase patterns from `db.py:25-99`

**1.1.4 – SessionContextManager Implementation**
- **Goal**: Implement per-session focused database context management with thread safety
- **Pre-conditions**: Task 1.1.2 complete (tests implemented and failing)
- **Success Gates**:
  - `mcp_arangodb_async/session_context.py` created
  - `SessionContextManager` class implemented
  - Thread-safe session context storage using `threading.Lock`
  - Session lifecycle management (set, get, clear, has_focused_database)
  - Database validation against configured databases
  - All unit tests from 1.1.2 pass for SessionContextManager
  - Integration with MultiDatabaseConnectionManager validated

**1.1.5 – ConfigFileLoader and Pydantic Models Implementation**
- **Goal**: Implement YAML configuration file loading with Pydantic validation and environment variable support
- **Pre-conditions**: Task 1.1.2 complete (tests implemented and failing)
- **Success Gates**:
  - `mcp_arangodb_async/config_loader.py` created
  - `mcp_arangodb_async/config_models.py` created with Pydantic models
  - `ConfigFileLoader` class implemented with YAML parsing
  - `DatabaseConfig` and `ConfigFile` Pydantic models with validation
  - Environment variable reference support (password_env)
  - Backward compatibility with existing environment variables (ARANGO_URL, ARANGO_DB, etc.)
  - All unit tests from 1.1.2 pass for ConfigFileLoader
  - All integration tests from 1.1.2 pass
  - Test execution report generated and approved

---

## Phase 2: CLI Tool (Weeks 2-3)

**Version Target**: v0.3.4 (after all Phase 2 milestones complete)

**Objective**: Implement secure CLI-based configuration management tool for database CRUD operations and status inspection, with user documentation.

### Milestone 2.1: CLI Tool Implementation (1 week)

**Version Target**: v0.3.4 (first and only milestone of Phase 2)

**Tasks**:

**2.1.1 – Test Definition for CLI Tool**
- **Goal**: Define comprehensive test suite for CLI tool before implementation
- **Pre-conditions**: Milestone 1.1 complete (core infrastructure implemented and tested)
- **Success Gates**:
  - Test definition report created following org's reporting guidelines
  - CLI command tests defined (add, remove, list, update, test, status)
  - YAML file manipulation tests defined (create, update, delete entries)
  - Error handling tests defined (invalid inputs, missing files, permission errors)
  - Integration tests defined (CLI → ConfigFileLoader → YAML file)
  - User review and approval of test definition report

**2.1.2 – Test Implementation for CLI Tool**
- **Goal**: Implement all tests defined in 2.1.1 before CLI code implementation begins
- **Pre-conditions**: Task 2.1.1 complete (test definition approved)
- **Success Gates**:
  - All CLI command tests from 2.1.1 implemented
  - All YAML file manipulation tests from 2.1.1 implemented
  - All error handling tests from 2.1.1 implemented
  - All integration tests from 2.1.1 implemented
  - Tests run and FAIL (expected - CLI not implemented yet)
  - Test execution report generated showing failing tests
  - User review and approval of test implementation

**2.1.3 – CLI Implementation**
- **Goal**: Implement argparse-based CLI tool with all database management commands
- **Pre-conditions**: Task 2.1.2 complete (tests implemented and failing)
- **Success Gates**:
  - `mcp_arangodb_async/cli/db.py` created
  - argparse setup with subcommands (add, remove, list, update, test, status)
  - `handle_add()` command implemented (add database configuration)
  - `handle_remove()` command implemented (remove database configuration)
  - `handle_list()` command implemented (list all databases)
  - `handle_update()` command implemented (update database configuration)
  - `handle_test()` command implemented (test database connection)
  - `handle_status()` command implemented (show configuration status with connection testing)
  - All CLI tests from 2.1.2 pass
  - Follows existing argparse patterns from `__main__.py:15-70`

**2.1.4 – CLI Integration and Entry Point**
- **Goal**: Integrate CLI tool with project build system and validate end-to-end functionality
- **Pre-conditions**: Task 2.1.3 complete (CLI implementation tested)
- **Success Gates**:
  - CLI entry point added to `pyproject.toml` console scripts
  - CLI accessible via `mcp-arangodb-async db` command
  - YAML file correctly created/updated/deleted by CLI commands
  - File permissions set correctly (600 for config file, 700 for config directory)
  - All integration tests from 2.1.2 pass
  - Test execution report generated and approved

**2.1.5 – CLI Tool User Documentation**
- **Goal**: Document CLI tool for end users following repo's documentation standards
- **Pre-conditions**: Task 2.1.4 complete (CLI tool fully functional)
- **Success Gates**:
  - Read and apply `docs/STYLE_GUIDE.md` standards (educational tone, progressive structure, actionable content)
  - Determine optimal integration point in existing documentation structure (analyze `docs/` directory)
  - Identify CRUD operation: CREATE new CLI documentation section OR UPDATE existing configuration documentation
  - Document all CLI commands (`mcp-arangodb-async db add/remove/list/update/test/status`)
  - Include command syntax, parameters, examples, expected output
  - Include common use cases and troubleshooting
  - Documentation integrated into existing docs at identified integration point
  - Documentation reviewed and approved

---

## Phase 3: Context Management & Status Tools (Weeks 3-4)

**Version Target**: v0.3.5 (after all Phase 3 milestones complete)

**Objective**: Implement 6 MCP tools for database context management and comprehensive status reporting, with API reference documentation.

### Milestone 3.1: Context Management Tools (0.5 weeks)

**Version Target**: v0.3.5 (first milestone of Phase 3)

**Tasks**:

**3.1.1 – Test Definition for Context Management Tools**
- **Goal**: Define comprehensive test suite for 3 context management MCP tools before implementation
- **Pre-conditions**: Milestone 2.1 complete (CLI tool implemented and tested)
- **Success Gates**:
  - Test definition report created following org's reporting guidelines
  - Tests defined for `set_focused_database()` tool (validation, session storage, error handling)
  - Tests defined for `get_focused_database()` tool (session retrieval, no session case)
  - Tests defined for `list_available_databases()` tool (database enumeration, no credentials exposed)
  - Integration tests defined (tool call → SessionContextManager → response)
  - Edge case tests defined (invalid database name, concurrent sessions, session cleanup)
  - User review and approval of test definition report

**3.1.2 – Test Implementation for Context Management Tools**
- **Goal**: Implement all tests defined in 3.1.1 before MCP tool code implementation begins
- **Pre-conditions**: Task 3.1.1 complete (test definition approved)
- **Success Gates**:
  - All tests from 3.1.1 implemented for `set_focused_database()` tool
  - All tests from 3.1.1 implemented for `get_focused_database()` tool
  - All tests from 3.1.1 implemented for `list_available_databases()` tool
  - All integration tests from 3.1.1 implemented
  - All edge case tests from 3.1.1 implemented
  - Tests run and FAIL (expected - tools not implemented yet)
  - Test execution report generated showing failing tests
  - User review and approval of test implementation

**3.1.3 – Context Management Tools Implementation**
- **Goal**: Implement 3 MCP tools for database context management
- **Pre-conditions**: Task 3.1.2 complete (tests implemented and failing)
- **Success Gates**:
  - Tool models created in `mcp_arangodb_async/models.py` (SetFocusedDatabaseArgs, GetFocusedDatabaseArgs, ListAvailableDatabasesArgs)
  - `set_focused_database()` handler implemented in `mcp_arangodb_async/handlers.py`
  - `get_focused_database()` handler implemented
  - `list_available_databases()` handler implemented (read-only, no credentials)
  - Tools registered in TOOL_REGISTRY
  - Tool descriptions updated
  - All unit tests from 3.1.2 pass
  - Integration tests from 3.1.2 pass

### Milestone 3.2: Status Reporting Tools (0.5 weeks)

**Version Target**: v0.3.5 (second milestone of Phase 3)

**Tasks**:

**3.2.1 – Test Definition for Status Reporting Tools**
- **Goal**: Define comprehensive test suite for 3 status reporting MCP tools before implementation
- **Pre-conditions**: Milestone 3.1 complete (context management tools implemented and tested)
- **Success Gates**:
  - Test definition report created following org's reporting guidelines
  - Tests defined for extended `arango_database_status()` tool (multi-database context, connection status)
  - Tests defined for `arango_database_resolution_status()` tool (6-level priority preview, all resolution levels)
  - Tests defined for `arango_list_database_configs()` tool (all databases with connection status)
  - Integration tests defined (tool call → MultiDatabaseConnectionManager → connection testing → response)
  - Edge case tests defined (connection failures, missing databases, invalid configurations)
  - User review and approval of test definition report

**3.2.2 – Test Implementation for Status Reporting Tools**
- **Goal**: Implement all tests defined in 3.2.1 before status tool code implementation begins
- **Pre-conditions**: Task 3.2.1 complete (test definition approved)
- **Success Gates**:
  - All tests from 3.2.1 implemented for extended `arango_database_status()` tool
  - All tests from 3.2.1 implemented for `arango_database_resolution_status()` tool
  - All tests from 3.2.1 implemented for `arango_list_database_configs()` tool
  - All integration tests from 3.2.1 implemented
  - All edge case tests from 3.2.1 implemented
  - Tests run and FAIL (expected - tools not implemented yet)
  - Test execution report generated showing failing tests
  - User review and approval of test implementation

**3.2.3 – Status Reporting Tools Implementation**
- **Goal**: Implement 3 MCP tools for comprehensive database status reporting
- **Pre-conditions**: Task 3.2.2 complete (tests implemented and failing)
- **Success Gates**:
  - Existing `arango_database_status()` handler extended for multi-database context in `handlers.py:1725-1791`
  - `arango_database_resolution_status()` handler implemented (shows 6-level priority resolution)
  - `arango_list_database_configs()` handler implemented (lists all databases with connection testing)
  - Tool models created/updated in `models.py`
  - Tools registered in TOOL_REGISTRY
  - Tool descriptions updated
  - All unit tests from 3.2.2 pass
  - All integration tests from 3.2.2 pass
  - Test execution report generated and approved

**3.2.4 – MCP Tools API Reference Documentation**
- **Goal**: Document all 6 MCP tools (3 context + 3 status) for end users and AI clients
- **Pre-conditions**: Task 3.2.3 complete (all 6 MCP tools fully functional)
- **Success Gates**:
  - Read and apply `docs/STYLE_GUIDE.md` standards (educational tone, progressive structure, actionable content)
  - Determine optimal integration point in existing documentation structure (analyze `docs/` directory)
  - Identify CRUD operation: UPDATE existing MCP tools documentation with new tools
  - Document all 6 MCP tools with parameters, return values, examples, use cases
  - Include context management workflow examples (set focused database → query → verify)
  - Include status reporting examples (check resolution, list configs, verify connection)
  - Documentation integrated into existing docs at identified integration point
  - Documentation reviewed and approved

---

## Phase 4: Tool Model Updates & Integration (Weeks 4-5)

**Version Target**: v0.3.6 (after all Phase 4 milestones complete)

**Objective**: Add optional database parameter to all 34 existing tools and integrate database resolution into server lifecycle, with developer architecture documentation.

### Milestone 4.1: Database Resolution Integration (0.5 weeks)

**Version Target**: v0.3.6 (first milestone of Phase 4)

**Tasks**:

**4.1.1 – Test Definition for Database Resolution**
- **Goal**: Define comprehensive test suite for database resolution algorithm and server lifecycle integration
- **Pre-conditions**: Milestone 3.2 complete (all 6 MCP tools implemented and tested)
- **Success Gates**:
  - Test definition report created following org's reporting guidelines
  - Tests defined for `resolve_database()` function (6-level priority algorithm)
  - Tests defined for updated `server_lifespan()` (multi-database context initialization)
  - Tests defined for updated `call_tool()` (database resolution, connection retrieval, tool execution)
  - Tests defined for session ID extraction (stdio and HTTP transports)
  - Integration tests defined (full request flow: tool call → resolution → connection → execution)
  - Edge case tests defined (missing session, invalid database, connection failures, fallback scenarios)
  - User review and approval of test definition report

**4.1.2 – Test Implementation for Database Resolution**
- **Goal**: Implement all tests defined in 4.1.1 before database resolution code implementation begins
- **Pre-conditions**: Task 4.1.1 complete (test definition approved)
- **Success Gates**:
  - All tests from 4.1.1 implemented for `resolve_database()` function
  - All tests from 4.1.1 implemented for updated `server_lifespan()`
  - All tests from 4.1.1 implemented for updated `call_tool()`
  - All tests from 4.1.1 implemented for session ID extraction
  - All integration tests from 4.1.1 implemented
  - All edge case tests from 4.1.1 implemented
  - Tests run and FAIL (expected - database resolution not implemented yet)
  - Test execution report generated showing failing tests
  - User review and approval of test implementation

**4.1.3 – Database Resolution Implementation**
- **Goal**: Implement database resolution algorithm and integrate into server lifecycle
- **Pre-conditions**: Task 4.1.2 complete (tests implemented and failing)
- **Success Gates**:
  - `resolve_database()` function implemented with 6-level priority algorithm
  - `server_lifespan()` refactored in `entry.py:157-221` for multi-database context
  - `call_tool()` updated in `entry.py:324-420` with database resolution
  - Session ID extraction implemented for stdio and HTTP transports
  - Database connection retrieval from MultiDatabaseConnectionManager
  - All unit tests from 4.1.2 pass
  - All integration tests from 4.1.2 pass

### Milestone 4.2: Tool Model Updates (0.5 weeks)

**Version Target**: v0.3.6 (second milestone of Phase 4)

**Tasks**:

**4.2.1 – Test Definition for Tool Model Updates**
- **Goal**: Define test suite for optional database parameter in all 34 tools
- **Pre-conditions**: Milestone 4.1 complete (database resolution integrated)
- **Success Gates**:
  - Test definition report created following org's reporting guidelines
  - Tests defined for optional database parameter in representative tools (query, collection, document)
  - Tests defined for database override behavior (tool arg overrides session context)
  - Regression tests defined (existing functionality without database parameter)
  - Integration tests defined (database parameter → resolution → correct database used)
  - User review and approval of test definition report

**4.2.2 – Test Implementation for Tool Model Updates**
- **Goal**: Implement all tests defined in 4.2.1 before tool model code changes begin
- **Pre-conditions**: Task 4.2.1 complete (test definition approved)
- **Success Gates**:
  - All tests from 4.2.1 implemented for optional database parameter
  - All tests from 4.2.1 implemented for database override behavior
  - All regression tests from 4.2.1 implemented
  - All integration tests from 4.2.1 implemented
  - Tests run and FAIL (expected - tool models not updated yet)
  - Test execution report generated showing failing tests
  - User review and approval of test implementation

**4.2.3 – Tool Model Updates Implementation**
- **Goal**: Add optional database parameter to all 34 existing tool Pydantic models
- **Pre-conditions**: Task 4.2.2 complete (tests implemented and failing)
- **Success Gates**:
  - `database: Optional[str]` field added to all 34 tool Pydantic models
  - Tool descriptions updated to mention optional database parameter
  - Tool documentation updated
  - All unit tests from 4.2.2 pass
  - All regression tests from 4.2.2 pass
  - All integration tests from 4.2.2 pass
  - Backward compatibility validated (existing tool calls work without database parameter)
  - Test execution report generated and approved

**4.2.4 – Developer Architecture Documentation**
- **Goal**: Document multi-database architecture for developers and contributors
- **Pre-conditions**: Task 4.2.3 complete (all tool models updated and tested)
- **Success Gates**:
  - Read and apply `docs/STYLE_GUIDE.md` standards (educational tone, progressive structure, actionable content)
  - Determine optimal integration point in existing documentation structure (analyze `docs/` directory)
  - Identify CRUD operation: CREATE new architecture documentation OR UPDATE existing developer docs
  - Document MultiDatabaseConnectionManager architecture (connection pooling, thread safety, lifecycle)
  - Document SessionContextManager architecture (session storage, focused database context, thread safety)
  - Document ConfigFileLoader architecture (YAML parsing, Pydantic validation, env var integration)
  - Document database resolution algorithm (6-level priority, decision tree, fallback logic)
  - Include architecture diagrams (Mermaid), code examples, design rationale
  - Documentation integrated into existing docs at identified integration point
  - Documentation reviewed and approved

---

## Phase 5: Testing, Security & Documentation (Weeks 5-5.5)

**Version Target**: v0.4.0 (Multi-Tenancy MVP - Production Release)

**Objective**: Comprehensive end-to-end testing, security audit, performance validation, and release preparation.

### Milestone 5.1: End-to-End Testing & Security (0.5 weeks)

**Version Target**: v0.4.0 (first milestone of Phase 5)

**Tasks**:

**5.1.1 – End-to-End Integration Tests**
- **Goal**: Validate complete multi-tenancy workflows from LLM agent perspective
- **Pre-conditions**: Milestone 4.2 complete (all tool models updated and tested)
- **Success Gates**:
  - E2E test scenarios defined and implemented:
    - Scenario 1: Set focused database → query → verify correct database used
    - Scenario 2: Query with database override → verify override works
    - Scenario 3: Multiple sessions with different focused databases → verify isolation
    - Scenario 4: Database resolution priority → verify 6-level algorithm
    - Scenario 5: Backward compatibility → verify environment variable configuration works
  - All E2E tests pass
  - No regressions in existing functionality
  - Test execution report generated

**5.1.2 – Security Audit**
- **Goal**: Validate security posture of multi-tenancy implementation
- **Pre-conditions**: Task 5.1.1 complete (E2E tests passing)
- **Success Gates**:
  - Credential management audit complete (no passwords in config file, only env var references)
  - CLI access control validated (file permissions 600 for config, 700 for directory)
  - MCP tool security validated (no credential exposure via list_available_databases)
  - Connection pool security validated (connection limits, credential validation)
  - Audit logging validated (configuration changes, database access, focused database changes)
  - Security audit report generated and approved

**5.1.3 – Performance Testing**
- **Goal**: Validate performance characteristics of multi-database connection pool and session management
- **Pre-conditions**: Task 5.1.2 complete (security audit passed)
- **Success Gates**:
  - Connection pool performance benchmarked (connection creation, reuse, cleanup)
  - Session management performance benchmarked (concurrent sessions, context switching)
  - Database resolution performance benchmarked (6-level priority algorithm overhead)
  - Performance targets met (≤5% overhead vs. single-database baseline)
  - Performance test report generated and approved

### Milestone 5.2: Release Preparation (0.5 weeks)

**Version Target**: v0.4.0 (final release milestone)

**Tasks**:

**5.2.1 – Migration Guide**
- **Goal**: Create migration guide for existing users transitioning from environment variables to YAML config
- **Pre-conditions**: Milestone 5.1 complete (testing, security, performance validated)
- **Success Gates**:
  - Read and apply `docs/STYLE_GUIDE.md` standards (educational tone, progressive structure, actionable content)
  - Migration guide created with step-by-step instructions
  - Before/after examples showing environment variable config vs. YAML config
  - Backward compatibility clearly explained (environment variables still work)
  - Common migration scenarios documented (single database, multiple databases, multi-server)
  - Troubleshooting section for migration issues
  - Migration guide integrated into documentation
  - Migration guide reviewed and approved

**5.2.2 – Deployment Guide**
- **Goal**: Create deployment guide for multi-database setups
- **Pre-conditions**: Task 5.2.1 complete (migration guide created)
- **Success Gates**:
  - Read and apply `docs/STYLE_GUIDE.md` standards (educational tone, progressive structure, actionable content)
  - Deployment guide created for multi-database configurations
  - Deployment scenarios documented (single server multiple databases, multiple servers, geo-distributed, hybrid)
  - Docker Compose examples for multi-database setups
  - Security best practices for production deployments
  - Monitoring and logging recommendations
  - Deployment guide integrated into documentation
  - Deployment guide reviewed and approved

**5.2.3 – Troubleshooting Guide**
- **Goal**: Create troubleshooting guide for common multi-tenancy issues
- **Pre-conditions**: Task 5.2.2 complete (deployment guide created)
- **Success Gates**:
  - Read and apply `docs/STYLE_GUIDE.md` standards (educational tone, progressive structure, actionable content)
  - Troubleshooting guide created with common issues and solutions
  - Database resolution issues documented (wrong database selected, resolution priority confusion)
  - Connection issues documented (connection failures, credential errors, timeout issues)
  - Configuration issues documented (invalid YAML, missing env vars, permission errors)
  - Session management issues documented (session lost, concurrent session conflicts)
  - Error messages explained with resolution steps
  - Troubleshooting guide integrated into documentation
  - Troubleshooting guide reviewed and approved

**5.2.4 – Release Preparation**
- **Goal**: Prepare v0.4.0 release with complete validation and release artifacts
- **Pre-conditions**: Task 5.2.3 complete (troubleshooting guide created)
- **Success Gates**:
  - All tests pass (unit, integration, E2E, regression, performance)
  - All documentation complete and accurate
  - CHANGELOG.md updated with v0.4.0 release notes
  - Version bumped to v0.4.0 in pyproject.toml
  - Git tag v0.4.0 created
  - Release notes prepared (features, breaking changes, migration guide link)
  - PyPI publishing validated (dry-run)
  - Knowledge transfer report generated following org's reporting guidelines
  - Final release approval obtained

---

## Deferred Features (v0.5.0+)

The following features are explicitly deferred to future releases to maintain focus on multi-tenancy MVP (v0.4.0):

### 1. Advanced Connection Pool Management (v0.5.0)

**Rationale**: v0.4.0 uses basic connection pooling with simple connection reuse. Advanced features like connection health checks, automatic reconnection, and connection pool sizing are not critical for MVP.

**Deferred Features**:
- Connection health checks (periodic ping to validate connections)
- Automatic reconnection on connection failures
- Connection pool sizing configuration (min/max connections per database)
- Connection timeout and idle connection cleanup
- Connection pool metrics and monitoring

**Estimated Effort**: 1 week

### 2. Multi-User Access Control (v0.5.0)

**Rationale**: v0.4.0 assumes single-user or admin-controlled configuration. Multi-user scenarios with per-user database access control are not required for MVP.

**Deferred Features**:
- Per-user database access control lists (ACLs)
- User authentication and authorization
- Role-based access control (RBAC) for database access
- Audit logging for user actions
- User session management

**Estimated Effort**: 2 weeks

### 3. Dynamic Database Discovery (v0.6.0)

**Rationale**: v0.4.0 requires explicit database configuration in YAML file. Dynamic discovery of databases from ArangoDB server is a convenience feature, not critical for MVP.

**Deferred Features**:
- Automatic database discovery from ArangoDB server
- Database metadata caching
- Database availability monitoring
- Automatic configuration updates on database changes

**Estimated Effort**: 1 week

### 4. Advanced CLI Features (v0.6.0)

**Rationale**: v0.4.0 CLI provides basic CRUD operations. Advanced features like interactive mode, configuration validation, and bulk operations are not critical for MVP.

**Deferred Features**:
- Interactive CLI mode (REPL-style database management)
- Configuration file validation and linting
- Bulk database operations (import/export configurations)
- CLI autocomplete and shell integration
- Configuration templates and presets

**Estimated Effort**: 1 week

### 5. Observability and Monitoring (v0.7.0)

**Rationale**: v0.4.0 includes basic logging. Advanced observability features like metrics, tracing, and health checks are not critical for MVP.

**Deferred Features**:
- Prometheus metrics export (connection pool stats, query latency, error rates)
- OpenTelemetry tracing integration
- Health check endpoints (HTTP /health, /ready)
- Structured logging with correlation IDs
- Performance profiling and diagnostics

**Estimated Effort**: 1.5 weeks

---

## Success Criteria

### Phase-Level Success Criteria

**Phase 1 Success Criteria**:
- ✅ MultiDatabaseConnectionManager implemented with thread-safe connection pooling
- ✅ SessionContextManager implemented with per-session focused database context
- ✅ ConfigFileLoader implemented with YAML parsing and Pydantic validation
- ✅ All Phase 1 unit tests pass (100% coverage for new components)
- ✅ Integration tests pass (config load → connection creation → session management)

**Phase 2 Success Criteria**:
- ✅ CLI tool implemented with all 6 commands (add, remove, list, update, test, status)
- ✅ CLI accessible via `mcp-arangodb-async db` command
- ✅ YAML file correctly created/updated/deleted by CLI
- ✅ All Phase 2 unit and integration tests pass
- ✅ CLI tool user documentation complete and integrated

**Phase 3 Success Criteria**:
- ✅ 3 context management MCP tools implemented (set, get, list)
- ✅ 3 status reporting MCP tools implemented (status, resolution, list configs)
- ✅ All Phase 3 unit and integration tests pass
- ✅ MCP tools API reference documentation complete and integrated

**Phase 4 Success Criteria**:
- ✅ Database resolution algorithm implemented with 6-level priority
- ✅ Server lifecycle refactored for multi-database context
- ✅ All 34 existing tools updated with optional database parameter
- ✅ All Phase 4 unit, integration, and regression tests pass
- ✅ Developer architecture documentation complete and integrated

**Phase 5 Success Criteria**:
- ✅ All E2E tests pass (5 scenarios)
- ✅ Security audit passed (no credential exposure, proper access control)
- ✅ Performance targets met (≤5% overhead vs. baseline)
- ✅ Migration guide, deployment guide, troubleshooting guide complete
- ✅ v0.4.0 release artifacts ready (CHANGELOG, release notes, PyPI package)

### Overall Success Criteria (v0.4.0 Release)

**Functional Requirements**:
- ✅ Single MCP server instance manages multiple ArangoDB databases
- ✅ LLM agents can set focused database context via `set_focused_database()` tool
- ✅ All 34 existing tools support optional database parameter override
- ✅ Database resolution follows 6-level priority algorithm
- ✅ CLI tool provides secure admin-controlled configuration management
- ✅ Status reporting tools provide comprehensive database resolution visibility

**Non-Functional Requirements**:
- ✅ Backward compatibility: Existing environment variable configuration works
- ✅ Security: No credentials in config file, only environment variable references
- ✅ Performance: ≤5% overhead vs. single-database baseline
- ✅ Thread safety: All components thread-safe for concurrent access
- ✅ Documentation: Complete user and developer documentation

**Quality Gates**:
- ✅ All tests pass (unit, integration, E2E, regression, performance)
- ✅ Code coverage ≥90% for new components
- ✅ No critical or high-severity security vulnerabilities
- ✅ All documentation reviewed and approved
- ✅ Release artifacts validated (PyPI dry-run successful)

---

## Task Dependencies and Topological Ordering

**Dependency Graph** (tasks can be parallelized if no dependency):

```
Phase 1:
  1.1.1 (test def) → 1.1.2 (test impl) → [1.1.3, 1.1.4, 1.1.5] (parallel code impl)

Phase 2:
  2.1.1 (test def) → 2.1.2 (test impl) → 2.1.3 (CLI impl) → 2.1.4 (CLI integration) → 2.1.5 (CLI docs)

Phase 3:
  3.1.1 (test def) → 3.1.2 (test impl) → 3.1.3 (context tools impl)
  3.2.1 (test def) → 3.2.2 (test impl) → 3.2.3 (status tools impl) → 3.2.4 (MCP tools docs)

  Note: Milestone 3.2 depends on Milestone 3.1 completion

Phase 4:
  4.1.1 (test def) → 4.1.2 (test impl) → 4.1.3 (database resolution impl)
  4.2.1 (test def) → 4.2.2 (test impl) → 4.2.3 (tool model updates impl) → 4.2.4 (architecture docs)

  Note: Milestone 4.2 depends on Milestone 4.1 completion

Phase 5:
  5.1.1 (E2E tests) → 5.1.2 (security audit) → 5.1.3 (performance testing)
  5.2.1 (migration guide) → 5.2.2 (deployment guide) → 5.2.3 (troubleshooting guide) → 5.2.4 (release prep)

  Note: Milestone 5.2 depends on Milestone 5.1 completion
```

**Parallelization Opportunities**:
- Phase 1: Tasks 1.1.3, 1.1.4, 1.1.5 can be implemented in parallel after 1.1.2 complete
- Phase 3: Milestones 3.1 and 3.2 are sequential (3.2 depends on 3.1)
- Phase 4: Milestones 4.1 and 4.2 are sequential (4.2 depends on 4.1)
- Phase 5: Milestones 5.1 and 5.2 are sequential (5.2 depends on 5.1)

**Critical Path** (longest dependency chain):
```
1.1.1 → 1.1.2 → 1.1.3 → 2.1.1 → 2.1.2 → 2.1.3 → 2.1.4 → 2.1.5 →
3.1.1 → 3.1.2 → 3.1.3 → 3.2.1 → 3.2.2 → 3.2.3 → 3.2.4 →
4.1.1 → 4.1.2 → 4.1.3 → 4.2.1 → 4.2.2 → 4.2.3 → 4.2.4 →
5.1.1 → 5.1.2 → 5.1.3 → 5.2.1 → 5.2.2 → 5.2.3 → 5.2.4
```

**Total Tasks**: 29 (6 test definition + 6 test implementation + 14 code implementation + 3 documentation)

---

## Timeline and Effort Estimation

**Total Duration**: 5.5 weeks (27.5 working days)

**Phase Breakdown**:

| Phase | Duration | Milestones | Tasks | Effort (days) |
|-------|----------|------------|-------|---------------|
| Phase 1: Core Infrastructure | 1.5 weeks | 1 | 5 | 7.5 |
| Phase 2: CLI Tool | 1 week | 1 | 5 | 5 |
| Phase 3: Context & Status Tools | 1 week | 2 | 8 | 5 |
| Phase 4: Tool Model Updates | 1 week | 2 | 7 | 5 |
| Phase 5: Testing & Release | 1 week | 2 | 7 | 5 |
| **Total** | **5.5 weeks** | **8** | **29** | **27.5** |

**Task-Level Effort Estimates**:

**Phase 1 (7.5 days)**:
- 1.1.1 Test Definition: 1 day
- 1.1.2 Test Implementation: 1 day
- 1.1.3 MultiDatabaseConnectionManager: 2 days
- 1.1.4 SessionContextManager: 1.5 days
- 1.1.5 ConfigFileLoader: 2 days

**Phase 2 (5 days)**:
- 2.1.1 Test Definition: 0.5 days
- 2.1.2 Test Implementation: 0.5 days
- 2.1.3 CLI Implementation: 2 days
- 2.1.4 CLI Integration: 1 day
- 2.1.5 CLI Documentation: 0.5 days

**Phase 3 (5 days)**:
- 3.1.1 Test Definition: 0.5 days
- 3.1.2 Test Implementation: 0.5 days
- 3.1.3 Context Tools Implementation: 1 day
- 3.2.1 Test Definition: 0.5 days
- 3.2.2 Test Implementation: 0.5 days
- 3.2.3 Status Tools Implementation: 1.5 days
- 3.2.4 MCP Tools Documentation: 0.5 days

**Phase 4 (5 days)**:
- 4.1.1 Test Definition: 0.5 days
- 4.1.2 Test Implementation: 0.5 days
- 4.1.3 Database Resolution Implementation: 1.5 days
- 4.2.1 Test Definition: 0.5 days
- 4.2.2 Test Implementation: 0.5 days
- 4.2.3 Tool Model Updates: 1 day
- 4.2.4 Architecture Documentation: 0.5 days

**Phase 5 (5 days)**:
- 5.1.1 E2E Tests: 1 day
- 5.1.2 Security Audit: 1 day
- 5.1.3 Performance Testing: 1 day
- 5.2.1 Migration Guide: 0.5 days
- 5.2.2 Deployment Guide: 0.5 days
- 5.2.3 Troubleshooting Guide: 0.5 days
- 5.2.4 Release Preparation: 0.5 days

**Assumptions**:
- Single developer working full-time (8 hours/day, 5 days/week)
- No major blockers or unexpected issues
- User review and approval cycles ≤1 day per deliverable
- Test-driven development workflow strictly followed
- Documentation written incrementally (not batched at end)

**Risk Buffer**: 0.5 weeks built into timeline for:
- Unexpected integration issues
- User feedback requiring rework
- Performance optimization needs
- Documentation revisions

---

## Appendix: Organizational Standards References

**Reporting Guidelines**: `cracking-shells-playbook/instructions/reporting.instructions.md`
- Report location: `Laghari/Augment/mcp-arangodb-async/multi_tenancy_analysis/`
- Naming convention: `<round_prefix>-<descriptive_name>_v<version>.md`
- README file convention with ⭐ CURRENT and 📦 ARCHIVED markers

**Roadmap Generation**: `cracking-shells-playbook/instructions/roadmap-generation.instructions.md`
- Phases → Milestones → Tasks structure
- Semantic versioning integration
- Git workflow integration

**Code Change Phases**: `cracking-shells-playbook/instructions/code-change-phases.instructions.md`
- 7-phase development workflow (Analysis → Test Definition → Implementation → Debugging → Git Commits → Documentation → Documentation Commits)

**Documentation Style Guide**: `docs/STYLE_GUIDE.md`
- Educational tone, progressive structure, actionable content
- Pedagogical patterns (Context → Concept → Code → Conclusion)
- Voice standards (active voice, present tense, direct address)

---

**End of Roadmap Document**


